<template>
  <div class="w-full max-w-5xl border-2 border-neutral-700 p-6 sm:p-10">
    
    <div class="text-center mb-10">
      <h1 class="text-3xl sm:text-4xl font-bold uppercase tracking-[0.3em]">Object Detection</h1>
      <p class="text-sm mt-2 text-neutral-400">// UPLOAD AN IMAGE TO SCAN</p>
    </div>

    <!-- Upload Section -->
    <div class="mb-8">
      <label
        class="cursor-target block border-2 border-dashed border-neutral-500 p-10 text-center transition-colors duration-300 hover:border-white hover:bg-neutral-900"
      >
        <input type="file" class="hidden" @change="onFileChange" accept="image/jpeg,image/png" :disabled="isLoading" />
        
        <div v-if="isLoading" class="flex flex-col items-center justify-center">
            <span class="text-lg uppercase tracking-widest text-neutral-400">ANALYZING...</span>
        </div>
        <div v-else class="flex flex-col items-center justify-center text-neutral-400">
          <span class="font-bold text-xl uppercase tracking-wider">> Select File <</span>
          <span class="text-sm mt-2">// CLICK OR DROP IMAGE HERE</span>
        </div>
      </label>
    </div>
    
    <div v-if="error" class="my-4 p-4 border-2 border-red-500 text-red-500">
      <span class="font-bold">// ERROR:</span> {{ error }}
    </div>

    <!-- Results Area -->
    <div v-if="imageUrl" class="grid grid-cols-1 md:grid-cols-5 gap-8 mt-12">
      <!-- The image itself can be a target -->
      <div class="cursor-target md:col-span-3 relative border-2 border-neutral-700">
        <img :src="imageUrl" ref="imgRef" @load="onImageLoad" class="block w-full h-auto" />
        <!-- This SVG now uses the 'detections' computed property -->
        <svg v-if="detections.length" :viewBox="`0 0 ${displayWidth} ${displayHeight}`" class="absolute top-0 left-0 w-full h-full pointer-events-none">
          <g v-for="(det, index) in detections" :key="index">
            <rect :x="det.x" :y="det.y" :width="det.width" :height="det.height" stroke="white" stroke-width="2" fill="transparent" />
            <rect :x="det.x" :y="Math.max(det.y - 18, 0)" :width="(det.label.length * 9 + 45)" height="16" fill="white" />
            <text :x="det.x + 5" :y="Math.max(det.y - 5, 11)" fill="black" font-size="12" font-weight="bold" class="uppercase">
              {{ det.label }} {{ (det.confidence * 100).toFixed(0) }}%
            </text>
          </g>
        </svg>
      </div>
      
      <!-- Summary Panel -->
      <div class="md:col-span-2 border-2 border-neutral-700 p-6">
        <!-- Show this whole block only if there are results from the API -->
        <div v-if="allDetections.length > 0" class="h-full">
          <h2 class="text-xl font-bold uppercase tracking-wider border-b-2 border-neutral-700 pb-3 mb-4">// SCAN RESULTS</h2>
          
          <!-- NEW: Filter Checkboxes Section -->
          <div class="mb-6">
            <h3 class="uppercase text-neutral-400 mb-2 text-sm">// FILTER VISIBILITY</h3>
            <div class="flex flex-wrap gap-x-6 gap-y-2">
              <label v-for="label in uniqueObjectLabels" :key="label" class="cursor-target flex items-center space-x-2 text-sm transition-colors hover:text-white">
                <input
                  type="checkbox"
                  :value="label"
                  v-model="visibleLabels"
                  class="cursor-target appearance-none w-4 h-4 border-2 border-neutral-500 bg-black checked:bg-white transition-colors"
                />
                <span class="uppercase">{{ label }}</span>
              </label>
            </div>
          </div>
          
          <!-- This part now reflects the filtered results -->
          <div class="border-t-2 border-neutral-700 pt-4">
            <div class="flex items-center justify-between text-base mb-6 font-bold">
              <span>VISIBLE_OBJECTS:</span>
              <span>{{ detections.length }}</span>
            </div>
            <ul class="space-y-3">
              <!-- objectCounts is also computed, so it's always up to date -->
              <li v-for="(count, label) in objectCounts" :key="label" class="flex justify-between items-center">
                <span class="uppercase">{{ label }}</span>
                <span>- [ {{ count }} ]</span>
              </li>
            </ul>
          </div>
        </div>
        
        <div v-else-if="!isLoading" class="h-full flex items-center justify-center text-neutral-500">
          <p class="text-center">// AWAITING SCAN</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup >

import { ref, computed } from 'vue';

// --- STATE MANAGEMENT ---
const imageFile = ref(null);
const imageUrl = ref(null);
const displayWidth = ref(0);
const displayHeight = ref(0);
const isLoading = ref(false);
const error = ref(null);
const apiKey = import.meta.env.VITE_API_KEY;

const imgRef = ref(null);

const allDetections = ref([]);
const visibleLabels = ref([]);

const detections = computed(() => {
  if (!allDetections.value.length || !visibleLabels.value.length) return [];
  return allDetections.value.filter(det => visibleLabels.value.includes(det.label));
});

const uniqueObjectLabels = computed(() => {
    if (!allDetections.value.length) return [];
    return [...new Set(allDetections.value.map(d => d.label))].sort();
});

const objectCounts = computed(() => {
  if (!detections.value.length) return {};
  return detections.value.reduce((acc, detection) => {
    const label = detection.label;
    acc[label] = (acc[label] || 0) + 1;
    return acc;
  }, {});
});

const onFileChange = (event) => {
  const file = event.target.files[0];
  if (!file) return;
  imageFile.value = file;
  imageUrl.value = URL.createObjectURL(imageFile.value);
  
  // Reset all relevant states
  allDetections.value = [];
  visibleLabels.value = [];
  error.value = null;
};

const onImageLoad = async () => {
  if (!imgRef.value) return;
  displayWidth.value = imgRef.value.clientWidth;
  displayHeight.value = imgRef.value.clientHeight;
  await detectObjects();
};

const detectObjects = async () => {
  if (!imageFile.value) return;
  isLoading.value = true;
  error.value = null;
  const formData = new FormData();
  formData.append('image', imageFile.value);

  try {
    const res = await fetch('https://api.api-ninjas.com/v1/objectdetection', {
      method: 'POST',
      headers: { 'X-Api-Key': apiKey },
      body: formData,
    });
    if (!res.ok) {
      const errorText = await res.text();
      throw new Error(`API returned status ${res.status}. ${errorText}`);
    }
    const json = await res.json();
    
    const { naturalWidth, naturalHeight } = imgRef.value;
    const scaleX = displayWidth.value / naturalWidth;
    const scaleY = displayHeight.value / naturalHeight;
    const CONF_THRESHOLD = 0.5;

    const mappedDetections = json
      .filter(obj => parseFloat(obj.confidence) >= CONF_THRESHOLD)
      .map(obj => {
        const x1 = parseFloat(obj.bounding_box.x1);
        const y1 = parseFloat(obj.bounding_box.y1);
        const x2 = parseFloat(obj.bounding_box.x2);
        const y2 = parseFloat(obj.bounding_box.y2);
        return {
          label: obj.label,
          confidence: parseFloat(obj.confidence),
          x: x1 * scaleX,
          y: y1 * scaleY,
          width: (x2 - x1) * scaleX,
          height: (y2 - y1) * scaleY,
        };
      });

    // ** UPDATE THE NEW STATE **
    // 1. Store the full results
    allDetections.value = mappedDetections;
    // 2. Set all labels to be visible by default
    visibleLabels.value = [...new Set(mappedDetections.map(d => d.label))];

  } catch (err) {
    console.error('Detection error:', err);
    error.value = err.message || 'An unknown error occurred.';
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped>
/* Custom style for the checkbox to match the theme */
input[type="checkbox"] {
  /* Add a small checkmark icon when checked */
  background-image: url("data:image/svg+xml,%3csvg viewBox='0 0 16 16' fill='black' xmlns='http://www.w3.org/2000/svg'%3e%3cpath d='M12.207 4.793a1 1 0 010 1.414l-5 5a1 1 0 01-1.414 0l-2-2a1 1 0 011.414-1.414L6.5 9.086l4.293-4.293a1 1 0 011.414 0z'/%3e%3c/svg%3e");
  background-size: 100% 100%;
  background-position: center;
  background-repeat: no-repeat;
}
</style>