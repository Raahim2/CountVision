<template>
  <div class="bg-black text-white min-h-screen w-full flex flex-col items-center justify-center p-4 sm:p-8 font-mono">
    
    <TargetCursor
        :spin-duration="4"
        :hide-default-cursor="true"
    />

    <ObjectDetector />

  </div>
</template>

<script setup lang="ts">
  // NOTE: You will need to create these two files in your /components/ folder
  import TargetCursor from "./components/Cursor.vue";
  import ObjectDetector from "./components/ObjectDetector.vue";
</script>

<style>
/* Global styles for the page */
body {
  margin: 0;
  padding: 0;
  font-family: 'Fira Code', monospace; /* Or any other mono font you like */
}
</style>