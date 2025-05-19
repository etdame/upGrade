<script>
  import { onMount, tick } from 'svelte';
  import { tweened } from 'svelte/motion';
  import { fade } from 'svelte/transition';

  // --- Health check ---
  let serverStatus = 'Connecting…';
  onMount(async () => {
    try {
      const res = await fetch('http://localhost:8000/health');
      serverStatus = res.ok
        ? (await res.json()).message
        : `Error ${res.status}`;
    } catch {
      serverStatus = 'Offline';
    }
  });

  // --- Modes ---
  let optimizeMode = false;

  // --- Form state ---
  let formData = {
    age: 18,
    gender: 1,
    study_hours_per_day: 4,
    social_media_hours: 2,
    netflix_hours: 1,
    part_time_job: 0,
    attendance_percentage: 90,
    sleep_hours: 7,
    diet_quality: 1,
    exercise_frequency: 1,
    internet_quality: 1,
    mental_health_rating: 5,
    extracurricular_participation: 1
  };
  let desiredScore = 85;          // only in optimize mode

  // --- Flags & results ---
  let loading    = false;
  let error      = '';
  let showResult = false;

  // For predict mode
  let animatedScore = tweened(0, { duration: 800 });

  // For optimize mode: array of { key, before, after, color, value }
  let changes = [];

  // Which keys use <select>
  const selectFields = new Set([
    'gender','diet_quality','exercise_frequency',
    'internet_quality','part_time_job',
    'extracurricular_participation'
  ]);

  // --- Predict handler ---
  async function handlePredict() {
    loading = true; error = ''; showResult = false;
    animatedScore.set(0);

    try {
      const res = await fetch('http://localhost:8000/predict', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify(formData)
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const { predicted_exam_score } = await res.json();
      showResult = true;
      animatedScore.set(predicted_exam_score);
      await tick();
      resultRef?.scrollIntoView({ behavior:'smooth', block:'start' });
    } catch(e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  // --- Optimize handler ---
  async function handleOptimize() {
    loading = true; error = ''; showResult = false;

    // Snapshot before
    const beforeData = { ...formData };

    try {
      const res = await fetch('http://localhost:8000/recommend', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({ ...formData, desired_score: desiredScore })
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const { updated_features } = await res.json();

      // Build changes[] with a tweened store and subscribe to fill .value
      changes = Object.entries(updated_features)
        .filter(([k,v]) => v !== beforeData[k])
        .map(([k,v]) => {
          const before = beforeData[k];
          const after  = v;
          const color  = after > before ? '#7f5af0' : '#b5a0f6';
          const store  = tweened(before, { duration: 800 });
          const change = { key:k, before, after, color, value: before };
          store.subscribe(val => change.value = val);
          // bump the store to after
          store.set(after);
          return change;
        });

      showResult = true;
      await tick();
      resultRef?.scrollIntoView({ behavior:'smooth', block:'start' });
    } catch(e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  let resultRef;
</script>

<main class="container">
  <!-- Health + Mode Toggle -->
  <div class="mb-4 flex justify-between items-center">
    <span class="server-status">Server: {serverStatus}</span>
    <label class="flex items-center space-x-2">
      <input type="checkbox" bind:checked={optimizeMode} class="toggle"/>
      <span>{optimizeMode ? 'Optimize Mode' : 'Predict Mode'}</span>
    </label>
  </div>

  <!-- Form -->
  <form on:submit|preventDefault={optimizeMode ? handleOptimize : handlePredict}>
    {#if optimizeMode}
      <div class="row">
        <label for="desired_score">Desired Score</label>
        <input
          id="desired_score"
          type="number"
          bind:value={desiredScore}
          min="0" max="100" step="0.1"
          class="input"
        />
      </div>
    {/if}

    {#each Object.entries(formData) as [key,value]}
      <div class="row">
        <label for={key}>
          {key.replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase())}
        </label>
        {#if selectFields.has(key)}
          <select id={key} bind:value={formData[key]} class="input">
            {#if key==='gender'}
              <option value="0">Female</option>
              <option value="1">Male</option>
              <option value="2">Other</option>
            {:else if key==='diet_quality'}
              <option value="0">Poor</option>
              <option value="1">Fair</option>
              <option value="2">Good</option>
            {:else if key==='exercise_frequency'}
              <option value="0">None</option>
              <option value="1">Some</option>
              <option value="2">Regular</option>
            {:else if key==='internet_quality'}
              <option value="0">Poor</option>
              <option value="1">Average</option>
              <option value="2">Good</option>
            {:else}
              <option value="0">No</option>
              <option value="1">Yes</option>
            {/if}
          </select>
        {:else}
          <input
            id={key}
            type="number"
            bind:value={formData[key]}
            min="0"
            class="input"
          />
        {/if}
      </div>
    {/each}

    <div class="button-row">
      <button type="submit" class="btn" disabled={loading}>
        {loading
          ? (optimizeMode ? 'Optimizing…' : 'Calculating…')
          : (optimizeMode ? 'Optimize Habits' : 'Predict Exam Score')}
      </button>
    </div>
  </form>

  {#if error}
    <div class="error">{error}</div>
  {/if}

  <!-- Results -->
  {#if showResult}
    <div bind:this={resultRef} class="mt-6 space-y-4">
      {#if !optimizeMode}
        <!-- Predict Mode -->
        <div in:fade class="result-card">
          <h2>🎓 Predicted Score</h2>
          <p class="score">{$animatedScore.toFixed(2)}%</p>
        </div>
      {:else}
        <!-- Optimize Mode -->
        <div in:fade class="space-y-2">
          <h2 class="text-lg font-semibold">🔧 Habit Adjustments</h2>
          {#each changes as {key,value,color} (key)}
            <div class="row">
              <label>{key.replace(/_/g,' ').replace(/\b\w/g,c=>c.toUpperCase())}</label>
              <div class="value" style="color:{color}">
                {value.toFixed(
                  key.includes('hours') || key==='attendance_percentage' ? 1 : 2
                )}
              </div>
            </div>
          {/each}
        </div>
      {/if}
    </div>
  {/if}
</main>

<style>
  /* leave empty if you’re importing src/app.css */
</style>
