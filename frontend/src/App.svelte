<script>
  import { onMount } from 'svelte';
  import { tweened } from 'svelte/motion';
  import { fade } from 'svelte/transition';

  // initial form state
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
  let prediction = null;
  let showResult = false;

  // tweened store for animated count-up
  const animatedScore = tweened(0, { duration: 1000 });

  async function handlePredict() {
    loading = true;
    error = '';
    showResult = false;
    prediction = null;
    animatedScore.set(0);

    try {
      const res = await fetch('http://localhost:8000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const { predicted_exam_score } = await res.json();
      prediction = predicted_exam_score;
      showResult = true;
      // start the count-up animation
      animatedScore.set(prediction);
    } catch (e) {
      error = e.message;
    } finally {
      loading = false;
    }
  }
</script>

<main class="max-w-xl mx-auto p-6 space-y-6">
  <!-- Server status badge here if you have it -->

  <form on:submit|preventDefault={handlePredict} class="space-y-4">
    <!-- Numeric inputs -->
    <div class="grid grid-cols-2 gap-4">
      <label>
        Age
        <input type="number" bind:value={formData.age} min="0" class="w-full p-2 border rounded" />
      </label>
      <label>
        Gender
        <select bind:value={formData.gender} class="w-full p-2 border rounded">
          <option value="0">Female</option>
          <option value="1">Male</option>
          <option value="2">Other</option>
        </select>
      </label>
      <label>
        Study Hours / Day
        <input type="number" bind:value={formData.study_hours_per_day} min="0" max="24" step="0.5" class="w-full p-2 border rounded" />
      </label>
      <label>
        Sleep Hours
        <input type="number" bind:value={formData.sleep_hours} min="0" max="24" step="0.5" class="w-full p-2 border rounded" />
      </label>
      <label>
        Social Media Hours
        <input type="number" bind:value={formData.social_media_hours} min="0" max="24" step="0.5" class="w-full p-2 border rounded" />
      </label>
      <label>
        Netflix Hours
        <input type="number" bind:value={formData.netflix_hours} min="0" max="24" step="0.5" class="w-full p-2 border rounded" />
      </label>
      <label>
        Attendance %
        <input type="number" bind:value={formData.attendance_percentage} min="0" max="100" step="0.1" class="w-full p-2 border rounded" />
      </label>
      <label>
        Mental Health (0–10)
        <input type="number" bind:value={formData.mental_health_rating} min="0" max="10" class="w-full p-2 border rounded" />
      </label>
    </div>

    <!-- Categorical / binary selects -->
    <div class="grid grid-cols-2 gap-4">
      <label>
        Diet Quality
        <select bind:value={formData.diet_quality} class="w-full p-2 border rounded">
          <option value="0">Poor</option>
          <option value="1">Fair</option>
          <option value="2">Good</option>
        </select>
      </label>
      <label>
        Exercise Frequency
        <select bind:value={formData.exercise_frequency} class="w-full p-2 border rounded">
          <option value="0">None</option>
          <option value="1">Some</option>
          <option value="2">Regular</option>
        </select>
      </label>
      <label>
        Internet Quality
        <select bind:value={formData.internet_quality} class="w-full p-2 border rounded">
          <option value="0">Poor</option>
          <option value="1">Average</option>
          <option value="2">Good</option>
        </select>
      </label>
      <label>
        Part-time Job
        <select bind:value={formData.part_time_job} class="w-full p-2 border rounded">
          <option value="0">No</option>
          <option value="1">Yes</option>
        </select>
      </label>
      <label>
        Extracurricular
        <select bind:value={formData.extracurricular_participation} class="w-full p-2 border rounded">
          <option value="0">No</option>
          <option value="1">Yes</option>
        </select>
      </label>
    </div>


    <button
      type="submit"
      class="w-full py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50"
      disabled={loading}
    >
      {loading ? 'Calculating…' : 'Predict Exam Score'}
    </button>
  </form>

  {#if error}
    <div class="text-red-600">Error: {error}</div>
  {/if}

  {#if showResult}
    <div
      in:fade={{ duration: 400 }}
      class="mt-6 p-6 bg-white rounded-lg shadow text-center"
    >
      <h2 class="text-xl font-semibold mb-2">🎓 Predicted Score</h2>
      <p class="text-6xl font-bold text-indigo-600">
        { $animatedScore.toFixed(2) }%
      </p>
    </div>
  {/if}
</main>
