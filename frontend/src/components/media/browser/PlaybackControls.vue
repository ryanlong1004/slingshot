<template>
  <div class="card">
    <div class="p-5 border-b border-gray-200">
      <h2 class="text-lg font-medium text-gray-900">Playback Controls</h2>
    </div>
    
    <div class="p-5 space-y-4">
      <div class="flex justify-between space-x-4">
        <button
          class="btn btn-danger flex-1"
          @click="handleStop"
          :disabled="!isPlaying || loading"
          :class="{ 'btn-disabled': !isPlaying || loading }"
        >
          <span v-if="loading && actionType === 'stop'">
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Stopping...
          </span>
          <span v-else>Stop Video</span>
        </button>
        
        <button
          class="btn btn-primary flex-1"
          @click="handleRestart"
          :disabled="!canRestart || loading"
          :class="{ 'btn-disabled': !canRestart || loading }"
        >
          <span v-if="loading && actionType === 'restart'">
            <svg class="animate-spin -ml-1 mr-2 h-4 w-4 text-white inline-block" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Restarting...
          </span>
          <span v-else>Restart Video</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue';

export default {
  name: 'PlaybackControls',
  props: {
    status: {
      type: Object,
      required: true
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['stop', 'restart'],
  setup(props, { emit }) {
    const actionType = ref(null);

    const isPlaying = computed(() => {
      return props.status.status === 'playing';
    });

    const canRestart = computed(() => {
      return props.status.video_path && !isPlaying.value;
    });

    const handleStop = async () => {
      if (!isPlaying.value || props.loading) return;
      actionType.value = 'stop';
      emit('stop');
    };

    const handleRestart = async () => {
      if (!canRestart.value || props.loading) return;
      actionType.value = 'restart';
      emit('restart');
    };

    return {
      actionType,
      isPlaying,
      canRestart,
      handleStop,
      handleRestart
    };
  }
};
</script>
