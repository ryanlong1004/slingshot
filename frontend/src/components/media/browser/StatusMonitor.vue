<template>
  <div class="card">
    <div class="p-5 border-b border-gray-200 flex justify-between items-center">
      <h2 class="text-lg font-medium text-gray-900">Player Status</h2>
      <button 
        class="text-gray-400 hover:text-gray-500"
        @click="refresh"
        :disabled="refreshing"
      >
        <svg 
          xmlns="http://www.w3.org/2000/svg" 
          class="h-5 w-5" 
          :class="{ 'animate-spin': refreshing }"
          viewBox="0 0 20 20" 
          fill="currentColor"
        >
          <path fill-rule="evenodd" d="M4 2a1 1 0 011 1v2.101a7.002 7.002 0 0111.601 2.566 1 1 0 11-1.885.666A5.002 5.002 0 005.999 7H9a1 1 0 010 2H4a1 1 0 01-1-1V3a1 1 0 011-1zm.008 9.057a1 1 0 011.276.61A5.002 5.002 0 0014.001 13H11a1 1 0 110-2h5a1 1 0 011 1v5a1 1 0 11-2 0v-2.101a7.002 7.002 0 01-11.601-2.566 1 1 0 01.61-1.276z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>
    
    <div class="p-5">
      <dl class="grid grid-cols-1 gap-x-4 gap-y-6 sm:grid-cols-2">
        <div class="sm:col-span-1">
          <dt class="text-sm font-medium text-gray-500">Status</dt>
          <dd class="mt-1 text-sm text-gray-900">
            <span 
              class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
              :class="statusClass"
            >
              {{ formatStatus(status.status) }}
            </span>
          </dd>
        </div>
        
        <div class="sm:col-span-1">
          <dt class="text-sm font-medium text-gray-500">Process ID</dt>
          <dd class="mt-1 text-sm text-gray-900">{{ status.pid || 'N/A' }}</dd>
        </div>
        
        <div class="sm:col-span-2">
          <dt class="text-sm font-medium text-gray-500">Video Path</dt>
          <dd class="mt-1 text-sm text-gray-900 break-all">{{ status.video_path || 'None' }}</dd>
        </div>
        
        <div class="sm:col-span-1">
          <dt class="text-sm font-medium text-gray-500">Uptime</dt>
          <dd class="mt-1 text-sm text-gray-900">{{ formatUptime(status.uptime) }}</dd>
        </div>
        
        <div v-if="status.error" class="sm:col-span-2">
          <dt class="text-sm font-medium text-red-500">Error</dt>
          <dd class="mt-1 text-sm text-red-500 break-all">{{ status.error }}</dd>
        </div>
      </dl>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue';

export default {
  name: 'StatusMonitor',
  props: {
    status: {
      type: Object,
      required: true
    },
    refreshing: {
      type: Boolean,
      default: false
    }
  },
  emits: ['refresh'],
  setup(props, { emit }) {
    const statusClass = computed(() => {
      switch (props.status.status) {
        case 'playing':
          return 'bg-green-100 text-green-800';
        case 'error':
          return 'bg-red-100 text-red-800';
        case 'stopped':
        default:
          return 'bg-gray-100 text-gray-800';
      }
    });

    const formatStatus = (status) => {
      if (!status) return 'Unknown';
      return status.charAt(0).toUpperCase() + status.slice(1);
    };

    const formatUptime = (seconds) => {
      if (!seconds) return 'N/A';
      
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      const secs = Math.floor(seconds % 60);
      
      return [
        hours.toString().padStart(2, '0'),
        minutes.toString().padStart(2, '0'),
        secs.toString().padStart(2, '0')
      ].join(':');
    };

    const refresh = () => {
      if (!props.refreshing) {
        emit('refresh');
      }
    };
    
    return {
      statusClass,
      formatStatus,
      formatUptime,
      refresh
    };
  }
};
</script>
