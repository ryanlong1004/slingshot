<template>
  <div class="card">
    <div class="p-5 border-b border-gray-200">
      <h2 class="text-lg font-medium text-gray-900">Select Video</h2>
    </div>
    
    <div class="p-5">
      <!-- Drag & Drop Upload Area -->
      <div 
        class="relative border-2 border-dashed rounded-md p-6 text-center"
        :class="[
          isDragging ? 'border-primary bg-primary bg-opacity-5' : 'border-gray-300 hover:border-gray-400',
          loading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
        ]"
        @dragover.prevent="handleDragOver"
        @dragleave.prevent="handleDragLeave"
        @drop.prevent="handleDrop"
        @click="!loading && browseLocalFile()"
      >
        <input 
          ref="fileInput"
          type="file"
          accept="video/*,.mkv,.avi,.mov,.mp4,.webm,.flv,.wmv,.3gp,.m4v,.mpg,.mpeg,.m2v"
          class="hidden"
          @change="handleFileSelect"
        />
        
        <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1">
          <path stroke-linecap="round" stroke-linejoin="round" d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />
        </svg>
        
        <span class="mt-2 block text-sm font-medium text-gray-900">
          {{ isDragging ? 'Drop video file here' : 'Drag and drop video file or click to browse' }}
        </span>
        
        <span class="mt-2 block text-xs text-gray-500">
          Supported formats: MP4, MKV, AVI, MOV, WEBM, FLV, etc.
        </span>
      </div>
      
      <!-- Manual Path Input -->
      <div class="mt-5">
        <label for="video-path" class="block text-sm font-medium text-gray-700 mb-1">
          Video Path
        </label>
        
        <div class="flex w-full">
          <input
            id="video-path"
            v-model="videoPath"
            type="text"
            class="form-input flex-grow rounded-r-none"
            placeholder="Enter video file path"
            :disabled="loading"
          />
          <button
            class="px-4 py-2 bg-gray-200 rounded-r-md border border-l-0 border-gray-300 hover:bg-gray-300 focus:outline-none focus:ring-primary focus:ring-1 disabled:opacity-50 disabled:cursor-not-allowed"
            @click="!loading && browseLocalFile()"
            :disabled="loading"
          >
            Browse
          </button>
        </div>
        
        <p v-if="pathError" class="mt-1 text-sm text-red-600">{{ pathError }}</p>
      </div>
      
      <!-- Playback options -->
      <div class="mt-5 grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="flex items-center">
          <input
            id="loop-video"
            v-model="playbackOptions.loop"
            type="checkbox"
            class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
            :disabled="loading"
          />
          <label for="loop-video" class="ml-2 block text-sm text-gray-900">
            Loop Video
          </label>
        </div>
        
        <div class="flex items-center">
          <input
            id="fullscreen"
            v-model="playbackOptions.fullscreen"
            type="checkbox"
            class="h-4 w-4 text-primary focus:ring-primary border-gray-300 rounded"
            :disabled="loading"
          />
          <label for="fullscreen" class="ml-2 block text-sm text-gray-900">
            Fullscreen Mode
          </label>
        </div>
      </div>
      
      <!-- Play button -->
      <div class="flex justify-end mt-5">
        <button
          class="btn btn-primary"
          @click="playVideo"
          :disabled="!isValidPath || loading"
          :class="{ 'btn-disabled': !isValidPath || loading }"
        >
          <span v-if="loading">
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Playing...
          </span>
          <span v-else>Play Video</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, reactive } from 'vue';

const VALID_VIDEO_EXTENSIONS = [
  '.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv', '.wmv', 
  '.3gp', '.m4v', '.mpg', '.mpeg', '.m2v', '.ts'
];

export default {
  name: 'VideoSelect',
  props: {
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['play-video', 'file-selected'],
  setup(props, { emit }) {
    const videoPath = ref('');
    const pathError = ref('');
    const fileInput = ref(null);
    const isDragging = ref(false);
    
    const playbackOptions = reactive({
      loop: true,
      fullscreen: true
    });

    const isValidPath = computed(() => {
      return videoPath.value && videoPath.value.trim() !== '';
    });

    const handleDragOver = () => {
      if (!props.loading) {
        isDragging.value = true;
      }
    };

    const handleDragLeave = () => {
      isDragging.value = false;
    };

    const handleDrop = (event) => {
      if (props.loading) return;
      
      isDragging.value = false;
      
      if (event.dataTransfer.files.length > 0) {
        const file = event.dataTransfer.files[0];
        handleFile(file);
      }
    };

    const handleFileSelect = (event) => {
      if (props.loading) return;
      
      if (event.target.files.length > 0) {
        const file = event.target.files[0];
        handleFile(file);
      }
    };

    const handleFile = (file) => {
      if (!file.type.startsWith('video/') && !hasValidExtension(file.name)) {
        pathError.value = 'Please select a valid video file';
        return;
      }

      pathError.value = '';
      videoPath.value = file.path;
      emit('file-selected', file.path);
    };

    const hasValidExtension = (filename) => {
      const lowerName = filename.toLowerCase();
      return VALID_VIDEO_EXTENSIONS.some(ext => lowerName.endsWith(ext));
    };

    const browseLocalFile = () => {
      if (fileInput.value) {
        fileInput.value.click();
      }
    };

    const playVideo = () => {
      if (!isValidPath.value) {
        pathError.value = 'Please select a video file';
        return;
      }

      emit('play-video', videoPath.value, playbackOptions);
    };

    return {
      videoPath,
      pathError,
      fileInput,
      isDragging,
      playbackOptions,
      isValidPath,
      handleDragOver,
      handleDragLeave,
      handleDrop,
      handleFileSelect,
      browseLocalFile,
      playVideo
    };
  }
};
</script>
