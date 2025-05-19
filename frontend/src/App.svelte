<script>
  import { onMount } from 'svelte';
  import { tweened } from 'svelte/motion';
  import { fade } from 'svelte/transition';

  // --- Health check ---
  let serverStatus = 'Connecting…';
  onMount(async () => {
    try {
      const res = await fetch('http://localhost:8000/health');
      if (res.ok) {
        const { message } = await res.json();
        serverStatus = message;
      } else {
        serverStatus = `Error ${res.status}`;
      }
    } catch {
      serverStatus = 'Offline';
    }
  });

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

  let loading = false;
  let error = '';
  let showResult = false;
  const animatedScore = tweened(0, { duration: 1000 });
  let resultRef;  // <--- ref for scrolling

  // --- Submit handler ---
  async function handlePredict() {
    loading = true;
    error = '';
    showResult = false;
    animatedScore.set(0);

    try {
      const res = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const { predicted_exam_score } = await res.json();

      // show and animate
      showResult = true;
      animatedScore.set(predicted_exam_score);

      // scroll into view
      await tick();  // wait for DOM update
      resultRef.scrollIntoView({ behavior: 'smooth', block: 'start' });

    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  import { tick } from 'svelte';
  const selectFields = new Set([
    'gender',
    'diet_quality',
    'exercise_frequency',
    'internet_quality',
    'part_time_job',
    'extracurricular_participation'
  ]);
</script>

<main class="container">
  <div class="mb-4">
    <span class="server-status">Server: {serverStatus}</span>
  </div>

  <form on:submit|preventDefault={handlePredict}>
    {#each Object.entries(formData) as [key, value]}
      <div class="row">
        <label for={key}>
          {key
            .replace(/_/g, ' ')
            .replace(/\b\w/g, c => c.toUpperCase())}
        </label>

        {#if selectFields.has(key)}
          <select id={key} bind:value={formData[key]} class="input">
            {#if key === 'gender'}
              <option value="0">Female</option>
              <option value="1">Male</option>
              <option value="2">Other</option>
            {:else if key === 'diet_quality'}
              <option value="0">Poor</option>
              <option value="1">Fair</option>
              <option value="2">Good</option>
            {:else if key === 'exercise_frequency'}
              <option value="0">None</option>
              <option value="1">Some</option>
              <option value="2">Regular</option>
            {:else if key === 'internet_quality'}
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
        {loading ? 'Calculating…' : 'Predict Exam Score'}
      </button>
    </div>
  </form>

  {#if error}
    <div class="error">{error}</div>
  {/if}

  {#if showResult}
    <div
      bind:this={resultRef}
      in:fade
      class="result-card"
    >
      <h2>🎓 Predicted Score</h2>
      <p class="score">{$animatedScore.toFixed(2)}%</p>
    </div>
  {/if}
</main>
