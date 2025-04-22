<template>
  <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
    <!-- Left column - Video Selection -->
    <div class="md:col-span-2">
      <VideoSelect :loading="loading" @play-video="playVideo" @file-selected="selectedFile = $event" />
    </div>

    <!-- Right column - Playback Controls and Status -->
    <div class="space-y-6">
      <StatusMonitor :status="playerStatus" :refreshing="refreshingStatus" @refresh="fetchPlayerStatus" />

      <PlaybackControls :status="playerStatus" :loading="loading" @stop="stopVideo" @restart="restartVideo" />
    </div>

    <!-- Notification/Alert area -->
    <div v-if="notification"
      class="fixed bottom-4 right-4 py-2 px-4 rounded-md shadow-lg transition-opacity duration-500"
      :class="notificationClass">
      {{ notification.message }}
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import VideoSelect from '@/components/media/browser/VideoSelect.vue';
import PlaybackControls from '@/components/media/browser/PlaybackControls.vue';
import StatusMonitor from '@/components/media/browser/StatusMonitor.vue';
import { playerApi } from '@/services/api';

export default {
  name: 'Home',
  components: {
    VideoSelect,
    PlaybackControls,
    StatusMonitor
  },
  setup() {
    // State
    const playerStatus = ref({
      status: 'stopped',
      video_path: null,
      pid: null,
      uptime: null,
      error: null
    });
    const loading = ref(false);
    const refreshingStatus = ref(false);
    const statusInterval = ref(null);
    const selectedFile = ref(null);
    const notification = ref(null);

    // Computed
    const notificationClass = computed(() => {
      if (!notification.value) return '';

      switch (notification.value.type) {
        case 'success':
          return 'bg-green-500 text-white';
        case 'error':
          return 'bg-red-500 text-white';
        case 'warning':
          return 'bg-yellow-500 text-white';
        default:
          return 'bg-blue-500 text-white';
      }
    });

    // Methods
    const fetchPlayerStatus = async () => {
      try {
        refreshingStatus.value = true;
        const response = await playerApi.getStatus();
        playerStatus.value = response.data;
      } catch (error) {
        console.error('Failed to fetch player status:', error);
        if (error.code === 'ERR_NETWORK') {
          showNotification('Network error: Unable to connect to the server', 'error');
        } else {
          showNotification('Failed to fetch player status', 'error');
        }
      } finally {
        refreshingStatus.value = false;
      }
    };

    const playVideo = async (videoPath, options = {}) => {
      console.log('Attempting to play video with path:', videoPath, 'and options:', options); // Debug log
      try {
        loading.value = true;
        const response = await playerApi.playVideo(videoPath, options);
        console.log('Backend response:', response.data); // Debug log
        playerStatus.value = response.data;
        showNotification('Video started successfully', 'success');
      } catch (error) {
        console.error('Failed to play video:', error);
        showNotification(error.response?.data?.detail || 'Failed to play video', 'error');
      } finally {
        loading.value = false;
      }
    };

    const stopVideo = async () => {
      try {
        loading.value = true;
        const response = await playerApi.stopVideo();
        playerStatus.value = response.data;
        showNotification('Video stopped', 'success');
      } catch (error) {
        console.error('Failed to stop video:', error);
        showNotification('Failed to stop video', 'error');
      } finally {
        loading.value = false;
      }
    };

    const restartVideo = async () => {
      try {
        loading.value = true;
        const response = await playerApi.restartVideo();
        playerStatus.value = response.data;
        showNotification('Video restarted', 'success');
      } catch (error) {
        console.error('Failed to restart video:', error);
        showNotification(error.response?.data?.detail || 'Failed to restart video', 'error');
      } finally {
        loading.value = false;
      }
    };

    const showNotification = (message, type = 'info') => {
      notification.value = { message, type };
      setTimeout(() => {
        notification.value = null;
      }, 3000);
    };

    // Lifecycle
    onMounted(() => {
      fetchPlayerStatus();
      // Set up polling for status
      statusInterval.value = setInterval(fetchPlayerStatus, 5000);
    });

    onUnmounted(() => {
      if (statusInterval.value) {
        clearInterval(statusInterval.value);
      }
    });

    return {
      playerStatus,
      loading,
      refreshingStatus,
      selectedFile,
      notification,
      notificationClass,
      fetchPlayerStatus,
      playVideo,
      stopVideo,
      restartVideo
    };
  }
};
</script>
