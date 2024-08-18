module.exports = {
    apps: [{
      name: "leetcode_bot",
      script: "./dist/index.js",
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: "1G",
      env_production: {
        NODE_ENV: "production",
      }
    }]
  }