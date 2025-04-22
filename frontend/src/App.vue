<template>
  <div class="min-h-screen bg-gray-100">
    <header class="bg-white shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex">
            <div class="flex-shrink-0 flex items-center">
              <h1 class="text-2xl font-bold text-primary">VLC Player Control</h1>
            </div>
            <nav class="ml-6 flex space-x-4">
              <router-link 
                to="/" 
                class="px-3 py-2 rounded-md text-sm font-medium"
                :class="[$route.path === '/' ? 'bg-primary text-white' : 'text-gray-500 hover:text-gray-700']"
              >
                Home
              </router-link>
              <router-link 
                to="/about" 
                class="px-3 py-2 rounded-md text-sm font-medium"
                :class="[$route.path === '/about' ? 'bg-primary text-white' : 'text-gray-500 hover:text-gray-700']"
              >
                About
              </router-link>
            </nav>
          </div>
        </div>
      </div>
    </header>

    <main>
      <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <router-view />
      </div>
    </main>

    <footer class="bg-white shadow-inner mt-8 py-4">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-gray-500 text-sm">
        VLC Player Control UI &copy; {{ new Date().getFullYear() }}
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>
