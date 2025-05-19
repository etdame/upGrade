<script>
  import { onMount } from 'svelte';

  let serverStatus = 'Connecting…';

  onMount(async () => {
    try {
      const res = await fetch('http://localhost:8000/health');
      if (res.ok) {
        const { message } = await res.json();
        serverStatus = message;           // should be "connected"
      } else {
        serverStatus = `Error ${res.status}`;
      }
    } catch (err) {
      serverStatus = 'Offline';
    }
  });
</script>

<main class="p-4">
  <!-- Pinned status badge -->
  <div class="mb-4">
    <span class="px-2 py-1 rounded bg-green-200 text-green-800">
      Server: {serverStatus}
    </span>
  </div>

  <!-- … the rest of your grade‐calculator / recommendation UI … -->
</main>