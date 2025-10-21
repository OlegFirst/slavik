import React from 'react';

const Untitled1 = () => {
  return (
    <div>
      
    
    <nav className="bg-white border-b border-gray-200 px-4 py-3 sm:px-6">
        <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="cog" className="lucide lucide-cog w-6 h-6 text-white"><path d="M11 10.27 7 3.34"></path><path d="m11 13.73-4 6.93"></path><path d="M12 22v-2"></path><path d="M12 2v2"></path><path d="M14 12h8"></path><path d="m17 20.66-1-1.73"></path><path d="m17 3.34-1 1.73"></path><path d="M2 12h2"></path><path d="m20.66 17-1.73-1"></path><path d="m20.66 7-1.73 1"></path><path d="m3.34 17 1.73-1"></path><path d="m3.34 7 1.73 1"></path><circle cx="12" cy="12" r="2"></circle><circle cx="12" cy="12" r="8"></circle></svg>
                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-gray-900">AI-Platform-ISO Admin</h1>
                        <p className="text-xs text-gray-500">System Settings</p>
                    </div>
                </div>
            </div>
            <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2 px-3 py-1 bg-success-100 text-success-800 rounded-full text-sm font-medium">
                    <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></div>
                    <span>System Healthy</span>
                </div>
                <button className="relative p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bell" className="lucide lucide-bell w-5 h-5"><path d="M10.268 21a2 2 0 0 0 3.464 0"></path><path d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326"></path></svg>
                    <div className="absolute -top-1 -right-1 w-3 h-3 bg-danger-500 rounded-full"></div>
                </button>
                <div className="flex items-center space-x-3 pl-3 border-l border-gray-200">
                    <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                        <span className="text-sm font-medium text-primary-600">SA</span>
                    </div>
                    <div className="hidden md:block">
                        <p className="text-sm font-medium text-gray-900">System Admin</p>
                        <p className="text-xs text-gray-500">Administrator</p>
                    </div>
                    <button className="p-1 text-gray-400 hover:text-gray-600">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="chevron-down" className="lucide lucide-chevron-down w-4 h-4"><path d="m6 9 6 6 6-6"></path></svg>
                    </button>
                </div>
            </div>
        </div>
    </nav>

    <div className="flex">
        
        <aside className="hidden lg:flex lg:flex-shrink-0">
            <div className="flex flex-col w-64 bg-white border-r border-gray-200">
                <div className="flex-1 flex flex-col pt-5 pb-4 overflow-y-auto">
                    <nav className="mt-5 flex-1 px-2 space-y-1">
                        <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="layout-dashboard" className="lucide lucide-layout-dashboard text-gray-400 mr-3 h-5 w-5"><rect width="7" height="9" x="3" y="3" rx="1"></rect><rect width="7" height="5" x="14" y="3" rx="1"></rect><rect width="7" height="9" x="14" y="12" rx="1"></rect><rect width="7" height="5" x="3" y="16" rx="1"></rect></svg>
                            Dashboard
                        </a>
                        <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="users" className="lucide lucide-users text-gray-400 mr-3 h-5 w-5"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path><path d="M16 3.128a4 4 0 0 1 0 7.744"></path><path d="M22 21v-2a4 4 0 0 0-3-3.87"></path><circle cx="9" cy="7" r="4"></circle></svg>
                            Users
                        </a>
                        <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="building" className="lucide lucide-building text-gray-400 mr-3 h-5 w-5"><path d="M12 10h.01"></path><path d="M12 14h.01"></path><path d="M12 6h.01"></path><path d="M16 10h.01"></path><path d="M16 14h.01"></path><path d="M16 6h.01"></path><path d="M8 10h.01"></path><path d="M8 14h.01"></path><path d="M8 6h.01"></path><path d="M9 22v-3a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v3"></path><rect x="4" y="2" width="16" height="20" rx="2"></rect></svg>
                            Organizations
                        </a>
                        <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="server" className="lucide lucide-server text-gray-400 mr-3 h-5 w-5"><rect width="20" height="8" x="2" y="2" rx="2" ry="2"></rect><rect width="20" height="8" x="2" y="14" rx="2" ry="2"></rect><line x1="6" x2="6.01" y1="6" y2="6"></line><line x1="6" x2="6.01" y1="18" y2="18"></line></svg>
                            Services
                        </a>
                        <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="cpu" className="lucide lucide-cpu text-gray-400 mr-3 h-5 w-5"><path d="M12 20v2"></path><path d="M12 2v2"></path><path d="M17 20v2"></path><path d="M17 2v2"></path><path d="M2 12h2"></path><path d="M2 17h2"></path><path d="M2 7h2"></path><path d="M20 12h2"></path><path d="M20 17h2"></path><path d="M20 7h2"></path><path d="M7 20v2"></path><path d="M7 2v2"></path><rect x="4" y="4" width="16" height="16" rx="2"></rect><rect x="8" y="8" width="8" height="8" rx="1"></rect></svg>
                            Infrastructure
                        </a>
                        <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="settings" className="lucide lucide-settings text-gray-400 mr-3 h-5 w-5"><path d="M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915"></path><circle cx="12" cy="12" r="3"></circle></svg>
                            Configuration
                        </a>
                        <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="file-text" className="lucide lucide-file-text text-gray-400 mr-3 h-5 w-5"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"></path><path d="M14 2v4a2 2 0 0 0 2 2h4"></path><path d="M10 9H8"></path><path d="M16 13H8"></path><path d="M16 17H8"></path></svg>
                            Logs &amp; Audit
                        </a>
                        <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="hard-drive" className="lucide lucide-hard-drive text-gray-400 mr-3 h-5 w-5"><line x1="22" x2="2" y1="12" y2="12"></line><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"></path><line x1="6" x2="6.01" y1="16" y2="16"></line><line x1="10" x2="10.01" y1="16" y2="16"></line></svg>
                            Backups
                        </a>
                        <a href="#" className="bg-primary-50 text-primary-700 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="cog" className="lucide lucide-cog text-primary-500 mr-3 h-5 w-5"><path d="M11 10.27 7 3.34"></path><path d="m11 13.73-4 6.93"></path><path d="M12 22v-2"></path><path d="M12 2v2"></path><path d="M14 12h8"></path><path d="m17 20.66-1-1.73"></path><path d="m17 3.34-1 1.73"></path><path d="M2 12h2"></path><path d="m20.66 17-1.73-1"></path><path d="m20.66 7-1.73 1"></path><path d="m3.34 17 1.73-1"></path><path d="m3.34 7 1.73 1"></path><circle cx="12" cy="12" r="2"></circle><circle cx="12" cy="12" r="8"></circle></svg>
                            System
                        </a>
                    </nav>
                </div>
            </div>
        </aside>

        
        <main className="flex-1 overflow-y-auto">
            <div className="py-6">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    
                    <div className="mb-8">
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900">System Settings</h1>
                                <p className="mt-1 text-sm text-gray-500">Configure system-wide settings, performance, and maintenance</p>
                            </div>
                            <div className="mt-4 sm:mt-0 flex space-x-3">
                                <button className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="download" className="lucide lucide-download w-4 h-4 mr-2"><path d="M12 15V3"></path><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><path d="m7 10 5 5 5-5"></path></svg>
                                    Export Config
                                </button>
                                <button className="bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="save" className="lucide lucide-save w-4 h-4 mr-2"><path d="M15.2 3a2 2 0 0 1 1.4.6l3.8 3.8a2 2 0 0 1 .6 1.4V19a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"></path><path d="M17 21v-7a1 1 0 0 0-1-1H8a1 1 0 0 0-1 1v7"></path><path d="M7 3v4a1 1 0 0 0 1 1h7"></path></svg>
                                    Save Changes
                                </button>
                            </div>
                        </div>
                    </div>

                    
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
                        <div className="flex items-center justify-between mb-6">
                            <div>
                                <h3 className="text-lg font-semibold text-gray-900">System Information</h3>
                                <p className="text-sm text-gray-500">Current platform version and environment details</p>
                            </div>
                            <div className="flex items-center space-x-2 px-3 py-1 bg-success-100 text-success-800 rounded-full text-sm font-medium">
                                <div className="w-2 h-2 bg-success-500 rounded-full"></div>
                                <span>Production</span>
                            </div>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                            <div className="bg-gray-50 rounded-lg p-4">
                                <div className="flex items-center space-x-3">
                                    <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="package" className="lucide lucide-package w-5 h-5 text-primary-600"><path d="M11 21.73a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73z"></path><path d="M12 22V12"></path><polyline points="3.29 7 12 12 20.71 7"></polyline><path d="m7.5 4.27 9 5.15"></path></svg>
                                    </div>
                                    <div>
                                        <p className="text-sm font-medium text-gray-500">Platform Version</p>
                                        <p className="text-lg font-bold text-gray-900">v2.0.0</p>
                                        <p className="text-xs text-gray-500">Build 2024.12.09</p>
                                    </div>
                                </div>
                            </div>
                            
                            <div className="bg-gray-50 rounded-lg p-4">
                                <div className="flex items-center space-x-3">
                                    <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="clock" className="lucide lucide-clock w-5 h-5 text-green-600"><path d="M12 6v6l4 2"></path><circle cx="12" cy="12" r="10"></circle></svg>
                                    </div>
                                    <div>
                                        <p className="text-sm font-medium text-gray-500">Uptime</p>
                                        <p className="text-lg font-bold text-gray-900">47d 12h</p>
                                        <p className="text-xs text-gray-500">Since last restart</p>
                                    </div>
                                </div>
                            </div>
                            
                            <div className="bg-gray-50 rounded-lg p-4">
                                <div className="flex items-center space-x-3">
                                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="globe" className="lucide lucide-globe w-5 h-5 text-blue-600"><circle cx="12" cy="12" r="10"></circle><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"></path><path d="M2 12h20"></path></svg>
                                    </div>
                                    <div>
                                        <p className="text-sm font-medium text-gray-500">Environment</p>
                                        <p className="text-lg font-bold text-gray-900">Production</p>
                                        <p className="text-xs text-gray-500">Kubernetes v1.28</p>
                                    </div>
                                </div>
                            </div>
                            
                            <div className="bg-gray-50 rounded-lg p-4">
                                <div className="flex items-center space-x-3">
                                    <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="shield-check" className="lucide lucide-shield-check w-5 h-5 text-purple-600"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"></path><path d="m9 12 2 2 4-4"></path></svg>
                                    </div>
                                    <div>
                                        <p className="text-sm font-medium text-gray-500">Security Level</p>
                                        <p className="text-lg font-bold text-gray-900">High</p>
                                        <p className="text-xs text-gray-500">TLS 1.3, 2FA</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                        <div className="border-b border-gray-200">
                            <nav className="flex space-x-8 px-6" aria-label="Tabs">
                                <button className="border-b-2 border-primary-500 py-4 px-1 text-sm font-medium text-primary-600 whitespace-nowrap" data-tab="performance">
                                    Performance
                                </button>
                                <button className="border-b-2 border-transparent py-4 px-1 text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap" data-tab="scaling">
                                    Scaling
                                </button>
                                <button className="border-b-2 border-transparent py-4 px-1 text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap" data-tab="maintenance">
                                    Maintenance
                                </button>
                                <button className="border-b-2 border-transparent py-4 px-1 text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap" data-tab="updates">
                                    Updates
                                </button>
                                <button className="border-b-2 border-transparent py-4 px-1 text-sm font-medium text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap" data-tab="license">
                                    License
                                </button>
                            </nav>
                        </div>

                        
                        <div id="performance-tab" className="tab-content p-6">
                            <div className="space-y-6">
                                <div>
                                    <h4 className="text-lg font-medium text-gray-900 mb-4">Performance Tuning</h4>
                                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                        <div className="space-y-4">
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-2">Worker Processes</label>
                                                <div className="flex items-center space-x-4">
                                                    <input type="range" min="1" max="16" value="8" className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer" />
                                                    <span className="text-sm font-medium text-gray-900 w-8">8</span>
                                                </div>
                                                <p className="text-xs text-gray-500 mt-1">Number of worker processes per service</p>
                                            </div>
                                            
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-2">Connection Pool Size</label>
                                                <div className="flex items-center space-x-4">
                                                    <input type="range" min="10" max="200" value="100" className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer" />
                                                    <span className="text-sm font-medium text-gray-900 w-12">100</span>
                                                </div>
                                                <p className="text-xs text-gray-500 mt-1">Database connection pool size</p>
                                            </div>
                                            
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-2">Cache TTL (seconds)</label>
                                                <input type="number" value="3600" min="60" max="86400" className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500" />
                                                <p className="text-xs text-gray-500 mt-1">Default cache time-to-live</p>
                                            </div>
                                        </div>
                                        
                                        <div className="space-y-4">
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-2">API Rate Limit (req/min)</label>
                                                <div className="flex items-center space-x-4">
                                                    <input type="range" min="100" max="10000" value="1000" className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer" />
                                                    <span className="text-sm font-medium text-gray-900 w-16">1000</span>
                                                </div>
                                                <p className="text-xs text-gray-500 mt-1">API requests per minute per user</p>
                                            </div>
                                            
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-2">Memory Limit (GB)</label>
                                                <div className="flex items-center space-x-4">
                                                    <input type="range" min="1" max="32" value="8" className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer" />
                                                    <span className="text-sm font-medium text-gray-900 w-8">8</span>
                                                </div>
                                                <p className="text-xs text-gray-500 mt-1">Memory limit per service instance</p>
                                            </div>
                                            
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-2">Query Timeout (seconds)</label>
                                                <input type="number" value="30" min="5" max="300" className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500" />
                                                <p className="text-xs text-gray-500 mt-1">Database query timeout</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div className="border-t border-gray-200 pt-6">
                                    <h4 className="text-lg font-medium text-gray-900 mb-4">Performance Monitoring</h4>
                                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                                        <div className="bg-gray-50 rounded-lg p-4">
                                            <div className="flex items-center justify-between">
                                                <span className="text-sm font-medium text-gray-700">Average Response Time</span>
                                                <span className="text-lg font-bold text-green-600">245ms</span>
                                            </div>
                                            <div className="mt-2 text-xs text-gray-500">Target: &lt; 500ms</div>
                                        </div>
                                        
                                        <div className="bg-gray-50 rounded-lg p-4">
                                            <div className="flex items-center justify-between">
                                                <span className="text-sm font-medium text-gray-700">Throughput</span>
                                                <span className="text-lg font-bold text-blue-600">1,247 req/s</span>
                                            </div>
                                            <div className="mt-2 text-xs text-gray-500">Peak: 2,100 req/s</div>
                                        </div>
                                        
                                        <div className="bg-gray-50 rounded-lg p-4">
                                            <div className="flex items-center justify-between">
                                                <span className="text-sm font-medium text-gray-700">Error Rate</span>
                                                <span className="text-lg font-bold text-green-600">0.02%</span>
                                            </div>
                                            <div className="mt-2 text-xs text-gray-500">Target: &lt; 0.1%</div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        
                        <div id="scaling-tab" className="tab-content p-6 hidden">
                            <div className="space-y-6">
                                <div>
                                    <h4 className="text-lg font-medium text-gray-900 mb-4">Auto-Scaling Configuration</h4>
                                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                        <div className="space-y-4">
                                            <div>
                                                <label className="flex items-center">
                                                    <input type="checkbox" checked="" className="text-primary-600 focus:ring-primary-500" />
                                                    <span className="ml-2 text-sm font-medium text-gray-700">Enable Auto-Scaling</span>
                                                </label>
                                                <p className="text-xs text-gray-500 mt-1 ml-6">Automatically scale services based on load</p>
                                            </div>
                                            
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-2">Minimum Replicas</label>
                                                <input type="number" value="2" min="1" max="10" className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500" />
                                            </div>
                                            
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-2">Maximum Replicas</label>
                                                <input type="number" value="10" min="2" max="50" className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500" />
                                            </div>
                                        </div>
                                        
                                        <div className="space-y-4">
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-2">CPU Threshold (%)</label>
                                                <div className="flex items-center space-x-4">
                                                    <input type="range" min="50" max="95" value="80" className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer" />
                                                    <span className="text-sm font-medium text-gray-900 w-8">80%</span>
                                                </div>
                                                <p className="text-xs text-gray-500 mt-1">Scale up when CPU usage exceeds this threshold</p>
                                            </div>
                                            
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-2">Memory Threshold (%)</label>
                                                <div className="flex items-center space-x-4">
                                                    <input type="range" min="50" max="95" value="85" className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer" />
                                                    <span className="text-sm font-medium text-gray-900 w-8">85%</span>
                                                </div>
                                                <p className="text-xs text-gray-500 mt-1">Scale up when memory usage exceeds this threshold</p>
                                            </div>
                                            
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-2">Scale Down Delay (minutes)</label>
                                                <input type="number" value="5" min="1" max="60" className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500" />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div className="border-t border-gray-200 pt-6">
                                    <h4 className="text-lg font-medium text-gray-900 mb-4">Load Balancing</h4>
                                    <div className="space-y-4">
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-2">Load Balancing Algorithm</label>
                                            <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                                                <option value="round-robin" selected="">Round Robin</option>
                                                <option value="least-connections">Least Connections</option>
                                                <option value="weighted-round-robin">Weighted Round Robin</option>
                                                <option value="ip-hash">IP Hash</option>
                                            </select>
                                        </div>
                                        
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                            <div>
                                                <label className="flex items-center">
                                                    <input type="checkbox" checked="" className="text-primary-600 focus:ring-primary-500" />
                                                    <span className="ml-2 text-sm font-medium text-gray-700">Health Checks</span>
                                                </label>
                                                <p className="text-xs text-gray-500 mt-1 ml-6">Enable automatic health checking</p>
                                            </div>
                                            
                                            <div>
                                                <label className="flex items-center">
                                                    <input type="checkbox" checked="" className="text-primary-600 focus:ring-primary-500" />
                                                    <span className="ml-2 text-sm font-medium text-gray-700">Session Affinity</span>
                                                </label>
                                                <p className="text-xs text-gray-500 mt-1 ml-6">Route requests to same instance</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        
                        <div id="maintenance-tab" className="tab-content p-6 hidden">
                            <div className="space-y-6">
                                <div>
                                    <h4 className="text-lg font-medium text-gray-900 mb-4">Maintenance Windows</h4>
                                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
                                        <div className="flex items-center">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="alert-triangle" className="lucide lucide-alert-triangle w-5 h-5 text-yellow-600 mr-2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>
                                            <span className="text-sm font-medium text-yellow-800">Next maintenance window: Sunday, 02:00 - 04:00 UTC</span>
                                        </div>
                                    </div>
                                    
                                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                        <div className="space-y-4">
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-2">Maintenance Day</label>
                                                <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                                                    <option value="sunday" selected="">Sunday</option>
                                                    <option value="monday">Monday</option>
                                                    <option value="tuesday">Tuesday</option>
                                                    <option value="wednesday">Wednesday</option>
                                                    <option value="thursday">Thursday</option>
                                                    <option value="friday">Friday</option>
                                                    <option value="saturday">Saturday</option>
                                                </select>
                                            </div>
                                            
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-2">Start Time</label>
                                                <input type="time" value="02:00" className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500" />
                                            </div>
                                            
                                            <div>
                                                <label className="block text-sm font-medium text-gray-700 mb-2">Duration (hours)</label>
                                                <input type="number" value="2" min="1" max="8" className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500" />
                                            </div>
                                        </div>
                                        
                                        <div className="space-y-4">
                                            <div>
                                                <label className="flex items-center">
                                                    <input type="checkbox" checked="" className="text-primary-600 focus:ring-primary-500" />
                                                    <span className="ml-2 text-sm font-medium text-gray-700">Auto-restart services</span>
                                                </label>
                                            </div>
                                            
                                            <div>
                                                <label className="flex items-center">
                                                    <input type="checkbox" checked="" className="text-primary-600 focus:ring-primary-500" />
                                                    <span className="ml-2 text-sm font-medium text-gray-700">Database optimization</span>
                                                </label>
                                            </div>
                                            
                                            <div>
                                                <label className="flex items-center">
                                                    <input type="checkbox" className="text-primary-600 focus:ring-primary-500" />
                                                    <span className="ml-2 text-sm font-medium text-gray-700">Clear cache</span>
                                                </label>
                                            </div>
                                            
                                            <div>
                                                <label className="flex items-center">
                                                    <input type="checkbox" checked="" className="text-primary-600 focus:ring-primary-500" />
                                                    <span className="ml-2 text-sm font-medium text-gray-700">Send notifications</span>
                                                </label>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div className="border-t border-gray-200 pt-6">
                                    <h4 className="text-lg font-medium text-gray-900 mb-4">Maintenance Mode</h4>
                                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="power" className="lucide lucide-power w-5 h-5 text-red-600 mr-2"><path d="M12 2v10"></path><path d="M18.4 6.6a9 9 0 1 1-12.77.04"></path></svg>
                                                <span className="text-sm font-medium text-red-800">Enable Maintenance Mode</span>
                                            </div>
                                            <button className="bg-red-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-red-700 transition-colors">
                                                Enable
                                            </button>
                                        </div>
                                        <p className="text-xs text-red-700 mt-2">This will put the platform in maintenance mode and display a maintenance page to users.</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        
                        <div id="updates-tab" className="tab-content p-6 hidden">
                            <div className="space-y-6">
                                <div>
                                    <h4 className="text-lg font-medium text-gray-900 mb-4">System Updates</h4>
                                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-6">
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="download" className="lucide lucide-download w-5 h-5 text-blue-600 mr-2"><path d="M12 15V3"></path><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><path d="m7 10 5 5 5-5"></path></svg>
                                                <div>
                                                    <span className="text-sm font-medium text-blue-800">Update Available: v2.1.0</span>
                                                    <p className="text-xs text-blue-700">Released: December 8, 2024</p>
                                                </div>
                                            </div>
                                            <button className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors">
                                                View Details
                                            </button>
                                        </div>
                                    </div>
                                    
                                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                        <div className="space-y-4">
                                            <div>
                                                <h5 className="text-sm font-medium text-gray-900 mb-2">Current Version</h5>
                                                <div className="bg-gray-50 rounded-lg p-3">
                                                    <div className="flex items-center justify-between">
                                                        <span className="text-sm text-gray-700">AI-Platform-ISO</span>
                                                        <span className="text-sm font-medium text-gray-900">v2.0.0</span>
                                                    </div>
                                                    <div className="text-xs text-gray-500 mt-1">Build: 2024.12.09.1547</div>
                                                </div>
                                            </div>
                                            
                                            <div>
                                                <h5 className="text-sm font-medium text-gray-900 mb-2">Update Settings</h5>
                                                <div className="space-y-2">
                                                    <label className="flex items-center">
                                                        <input type="checkbox" checked="" className="text-primary-600 focus:ring-primary-500" />
                                                        <span className="ml-2 text-sm text-gray-700">Auto-check for updates</span>
                                                    </label>
                                                    <label className="flex items-center">
                                                        <input type="checkbox" className="text-primary-600 focus:ring-primary-500" />
                                                        <span className="ml-2 text-sm text-gray-700">Auto-install security updates</span>
                                                    </label>
                                                    <label className="flex items-center">
                                                        <input type="checkbox" checked="" className="text-primary-600 focus:ring-primary-500" />
                                                        <span className="ml-2 text-sm text-gray-700">Backup before update</span>
                                                    </label>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div className="space-y-4">
                                            <div>
                                                <h5 className="text-sm font-medium text-gray-900 mb-2">Available Update: v2.1.0</h5>
                                                <div className="bg-green-50 rounded-lg p-3">
                                                    <div className="flex items-center justify-between mb-2">
                                                        <span className="text-sm font-medium text-green-800">New Features</span>
                                                        <span className="text-xs text-green-600">5 items</span>
                                                    </div>
                                                    <ul className="text-xs text-green-700 space-y-1">
                                                        <li>• Enhanced AI recommendations</li>
                                                        <li>• Improved dashboard performance</li>
                                                        <li>• New compliance templates</li>
                                                        <li>• Advanced risk analytics</li>
                                                        <li>• Mobile app improvements</li>
                                                    </ul>
                                                </div>
                                            </div>
                                            
                                            <div>
                                                <h5 className="text-sm font-medium text-gray-900 mb-2">Update Schedule</h5>
                                                <div className="space-y-2">
                                                    <label className="flex items-center">
                                                        <input type="radio" name="update-schedule" value="now" className="text-primary-600 focus:ring-primary-500" />
                                                        <span className="ml-2 text-sm text-gray-700">Install now</span>
                                                    </label>
                                                    <label className="flex items-center">
                                                        <input type="radio" name="update-schedule" value="maintenance" checked="" className="text-primary-600 focus:ring-primary-500" />
                                                        <span className="ml-2 text-sm text-gray-700">During next maintenance window</span>
                                                    </label>
                                                    <label className="flex items-center">
                                                        <input type="radio" name="update-schedule" value="custom" className="text-primary-600 focus:ring-primary-500" />
                                                        <span className="ml-2 text-sm text-gray-700">Schedule for later</span>
                                                    </label>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div className="border-t border-gray-200 pt-6">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <h4 className="text-lg font-medium text-gray-900">Release Notes</h4>
                                            <p className="text-sm text-gray-500">View detailed changelog and release information</p>
                                        </div>
                                        <button className="text-primary-600 hover:text-primary-700 text-sm font-medium flex items-center">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="external-link" className="lucide lucide-external-link w-4 h-4 mr-1"><path d="M15 3h6v6"></path><path d="M10 14 21 3"></path><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path></svg>
                                            View Full Changelog
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>

                        
                        <div id="license-tab" className="tab-content p-6 hidden">
                            <div className="space-y-6">
                                <div>
                                    <h4 className="text-lg font-medium text-gray-900 mb-4">License Information</h4>
                                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                                        <div className="space-y-4">
                                            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                                                <div className="flex items-center justify-between mb-2">
                                                    <span className="text-sm font-medium text-green-800">Enterprise License</span>
                                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                                                        Active
                                                    </span>
                                                </div>
                                                <div className="text-xs text-green-700">
                                                    <p>License Key: ENT-2024-XXXX-XXXX-XXXX</p>
                                                    <p>Expires: December 31, 2025</p>
                                                </div>
                                            </div>
                                            
                                            <div>
                                                <h5 className="text-sm font-medium text-gray-900 mb-2">Licensed Features</h5>
                                                <div className="space-y-2">
                                                    <div className="flex items-center justify-between">
                                                        <span className="text-sm text-gray-700">Unlimited Users</span>
                                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check" className="lucide lucide-check w-4 h-4 text-green-600"><path d="M20 6 9 17l-5-5"></path></svg>
                                                    </div>
                                                    <div className="flex items-center justify-between">
                                                        <span className="text-sm text-gray-700">AI Assistant</span>
                                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check" className="lucide lucide-check w-4 h-4 text-green-600"><path d="M20 6 9 17l-5-5"></path></svg>
                                                    </div>
                                                    <div className="flex items-center justify-between">
                                                        <span className="text-sm text-gray-700">Advanced Analytics</span>
                                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check" className="lucide lucide-check w-4 h-4 text-green-600"><path d="M20 6 9 17l-5-5"></path></svg>
                                                    </div>
                                                    <div className="flex items-center justify-between">
                                                        <span className="text-sm text-gray-700">Multi-tenant Support</span>
                                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check" className="lucide lucide-check w-4 h-4 text-green-600"><path d="M20 6 9 17l-5-5"></path></svg>
                                                    </div>
                                                    <div className="flex items-center justify-between">
                                                        <span className="text-sm text-gray-700">Premium Support</span>
                                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check" className="lucide lucide-check w-4 h-4 text-green-600"><path d="M20 6 9 17l-5-5"></path></svg>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div className="space-y-4">
                                            <div>
                                                <h5 className="text-sm font-medium text-gray-900 mb-2">Usage Statistics</h5>
                                                <div className="space-y-3">
                                                    <div>
                                                        <div className="flex items-center justify-between mb-1">
                                                            <span className="text-sm text-gray-700">Active Users</span>
                                                            <span className="text-sm font-medium text-gray-900">247 / Unlimited</span>
                                                        </div>
                                                        <div className="w-full bg-gray-200 rounded-full h-2">
                                                            <div className="bg-green-600 h-2 rounded-full" style={{width: '25%'}}></div>
                                                        </div>
                                                    </div>
                                                    
                                                    <div>
                                                        <div className="flex items-center justify-between mb-1">
                                                            <span className="text-sm text-gray-700">Organizations</span>
                                                            <span className="text-sm font-medium text-gray-900">12 / Unlimited</span>
                                                        </div>
                                                        <div className="w-full bg-gray-200 rounded-full h-2">
                                                            <div className="bg-blue-600 h-2 rounded-full" style={{width: '12%'}}></div>
                                                        </div>
                                                    </div>
                                                    
                                                    <div>
                                                        <div className="flex items-center justify-between mb-1">
                                                            <span className="text-sm text-gray-700">Storage Used</span>
                                                            <span className="text-sm font-medium text-gray-900">89.2 GB / 1 TB</span>
                                                        </div>
                                                        <div className="w-full bg-gray-200 rounded-full h-2">
                                                            <div className="bg-yellow-600 h-2 rounded-full" style={{width: '9%'}}></div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                            
                                            <div>
                                                <h5 className="text-sm font-medium text-gray-900 mb-2">Support Level</h5>
                                                <div className="bg-purple-50 border border-purple-200 rounded-lg p-3">
                                                    <div className="flex items-center justify-between">
                                                        <span className="text-sm font-medium text-purple-800">Premium Support</span>
                                                        <span className="text-xs text-purple-600">24/7</span>
                                                    </div>
                                                    <div className="text-xs text-purple-700 mt-1">
                                                        <p>• Priority support queue</p>
                                                        <p>• Dedicated account manager</p>
                                                        <p>• Phone &amp; email support</p>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div className="border-t border-gray-200 pt-6">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <h4 className="text-lg font-medium text-gray-900">License Management</h4>
                                            <p className="text-sm text-gray-500">Update license key or contact support for license changes</p>
                                        </div>
                                        <div className="flex space-x-3">
                                            <button className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors">
                                                Update License
                                            </button>
                                            <button className="bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors">
                                                Contact Support
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>

    
    <div className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-2 py-2">
        <div className="grid grid-cols-5 gap-1">
            <button className="flex flex-col items-center py-2 px-1 text-gray-400 hover:text-gray-600">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="layout-dashboard" className="lucide lucide-layout-dashboard w-5 h-5"><rect width="7" height="9" x="3" y="3" rx="1"></rect><rect width="7" height="5" x="14" y="3" rx="1"></rect><rect width="7" height="9" x="14" y="12" rx="1"></rect><rect width="7" height="5" x="3" y="16" rx="1"></rect></svg>
                <span className="text-xs mt-1">Dashboard</span>
            </button>
            <button className="flex flex-col items-center py-2 px-1 text-gray-400 hover:text-gray-600">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="users" className="lucide lucide-users w-5 h-5"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path><path d="M16 3.128a4 4 0 0 1 0 7.744"></path><path d="M22 21v-2a4 4 0 0 0-3-3.87"></path><circle cx="9" cy="7" r="4"></circle></svg>
                <span className="text-xs mt-1">Users</span>
            </button>
            <button className="flex flex-col items-center py-2 px-1 text-gray-400 hover:text-gray-600">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="server" className="lucide lucide-server w-5 h-5"><rect width="20" height="8" x="2" y="2" rx="2" ry="2"></rect><rect width="20" height="8" x="2" y="14" rx="2" ry="2"></rect><line x1="6" x2="6.01" y1="6" y2="6"></line><line x1="6" x2="6.01" y1="18" y2="18"></line></svg>
                <span className="text-xs mt-1">Services</span>
            </button>
            <button className="flex flex-col items-center py-2 px-1 text-gray-400 hover:text-gray-600">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="hard-drive" className="lucide lucide-hard-drive w-5 h-5"><line x1="22" x2="2" y1="12" y2="12"></line><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"></path><line x1="6" x2="6.01" y1="16" y2="16"></line><line x1="10" x2="10.01" y1="16" y2="16"></line></svg>
                <span className="text-xs mt-1">Backups</span>
            </button>
            <button className="flex flex-col items-center py-2 px-1 text-primary-600 bg-primary-50 rounded-lg">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="cog" className="lucide lucide-cog w-5 h-5"><path d="M11 10.27 7 3.34"></path><path d="m11 13.73-4 6.93"></path><path d="M12 22v-2"></path><path d="M12 2v2"></path><path d="M14 12h8"></path><path d="m17 20.66-1-1.73"></path><path d="m17 3.34-1 1.73"></path><path d="M2 12h2"></path><path d="m20.66 17-1.73-1"></path><path d="m20.66 7-1.73 1"></path><path d="m3.34 17 1.73-1"></path><path d="m3.34 7 1.73 1"></path><circle cx="12" cy="12" r="2"></circle><circle cx="12" cy="12" r="8"></circle></svg>
                <span className="text-xs mt-1 font-medium">System</span>
            </button>
        </div>
    </div>

    <script>
        // Initialize Lucide icons
        lucide.createIcons();
        
        document.addEventListener('DOMContentLoaded', function() {
            // Tab functionality
            const tabButtons = document.querySelectorAll('[data-tab]');
            const tabContents = document.querySelectorAll('.tab-content');
            
            tabButtons.forEach(button => {
                button.addEventListener('click', function() {
                    const targetTab = this.getAttribute('data-tab');
                    
                    // Remove active state from all tabs
                    tabButtons.forEach(btn => {
                        btn.classList.remove('border-primary-500', 'text-primary-600');
                        btn.classList.add('border-transparent', 'text-gray-500');
                    });
                    
                    // Add active state to clicked tab
                    this.classList.remove('border-transparent', 'text-gray-500');
                    this.classList.add('border-primary-500', 'text-primary-600');
                    
                    // Hide all tab contents
                    tabContents.forEach(content => {
                        content.classList.add('hidden');
                    });
                    
                    // Show target tab content
                    const targetContent = document.getElementById(targetTab + '-tab');
                    if (targetContent) {
                        targetContent.classList.remove('hidden');
                    }
                });
            });
            
            // Range slider updates
            const rangeInputs = document.querySelectorAll('input[type="range"]');
            rangeInputs.forEach(input => {
                const updateValue = () => {
                    const valueSpan = input.nextElementSibling;
                    if (valueSpan) {
                        let value = input.value;
                        if (input.getAttribute('min') === '100') {
                            // For rate limits, show as number
                            valueSpan.textContent = value;
                        } else if (input.getAttribute('max') === '95') {
                            // For percentages
                            valueSpan.textContent = value + '%';
                        } else {
                            valueSpan.textContent = value;
                        }
                    }
                };
                
                input.addEventListener('input', updateValue);
                updateValue(); // Set initial value
            });
            
            // Save Changes button
            const saveButton = document.querySelector('button:has(i[data-lucide="save"])');
            if (saveButton) {
                saveButton.addEventListener('click', function() {
                    console.log('Saving system settings...');
                    
                    // Show loading state
                    const icon = this.querySelector('i');
                    const text = this.lastChild;
                    const originalText = text.textContent;
                    
                    icon.setAttribute('data-lucide', 'loader');
                    text.textContent = 'Saving...';
                    this.disabled = true;
                    
                    lucide.createIcons();
                    
                    // Simulate save
                    setTimeout(() => {
                        icon.setAttribute('data-lucide', 'check');
                        text.textContent = 'Saved!';
                        
                        setTimeout(() => {
                            icon.setAttribute('data-lucide', 'save');
                            text.textContent = originalText;
                            this.disabled = false;
                            lucide.createIcons();
                        }, 2000);
                    }, 1500);
                });
            }
            
            // Export Config button
            const exportButton = document.querySelector('button:has(i[data-lucide="download"])');
            if (exportButton) {
                exportButton.addEventListener('click', function() {
                    console.log('Exporting configuration...');
                    // In real implementation, trigger config export
                });
            }
            
            // Maintenance Mode button
            const maintenanceButton = document.querySelector('.bg-red-600');
            if (maintenanceButton) {
                maintenanceButton.addEventListener('click', function() {
                    if (confirm('Are you sure you want to enable maintenance mode? This will make the platform unavailable to users.')) {
                        console.log('Enabling maintenance mode...');
                        // In real implementation, enable maintenance mode
                    }
                });
            }
            
            // Update buttons
            const viewDetailsButton = document.querySelector('.bg-blue-600');
            if (viewDetailsButton && viewDetailsButton.textContent.includes('View Details')) {
                viewDetailsButton.addEventListener('click', function() {
                    console.log('Viewing update details...');
                    // In real implementation, show update details modal
                });
            }
            
            // License buttons
            const updateLicenseButton = document.querySelector('button:contains("Update License")');
            const contactSupportButton = document.querySelector('button:contains("Contact Support")');
            
            document.querySelectorAll('button').forEach(button => {
                if (button.textContent.includes('Update License')) {
                    button.addEventListener('click', function() {
                        console.log('Opening license update dialog...');
                        // In real implementation, show license update modal
                    });
                }
                
                if (button.textContent.includes('Contact Support')) {
                    button.addEventListener('click', function() {
                        console.log('Opening support contact...');
                        // In real implementation, open support contact form
                    });
                }
            });
            
            // Form change handlers
            const formInputs = document.querySelectorAll('input, select');
            formInputs.forEach(input => {
                input.addEventListener('change', function() {
                    console.log(`Setting changed: ${this.name || this.type} = ${this.value || this.checked}`);
                    // In real implementation, mark form as dirty and enable save
                });
            });
            
            // Auto-save for critical settings
            const criticalSettings = document.querySelectorAll('input[type="checkbox"]');
            criticalSettings.forEach(checkbox => {
                checkbox.addEventListener('change', function() {
                    if (this.closest('#scaling-tab') && this.nextElementSibling.textContent.includes('Enable Auto-Scaling')) {
                        console.log(`Auto-scaling ${this.checked ? 'enabled' : 'disabled'}`);
                        // In real implementation, immediately apply auto-scaling changes
                    }
                });
            });
            
            // Keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                // Ctrl/Cmd + S to save
                if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                    e.preventDefault();
                    saveButton?.click();
                }
                
                // Ctrl/Cmd + E to export
                if ((e.ctrlKey || e.metaKey) && e.key === 'e') {
                    e.preventDefault();
                    exportButton?.click();
                }
                
                // Number keys to switch tabs
                if (e.key >= '1' && e.key <= '5' && (e.ctrlKey || e.metaKey)) {
                    e.preventDefault();
                    const tabIndex = parseInt(e.key) - 1;
                    const tabButton = tabButtons[tabIndex];
                    if (tabButton) {
                        tabButton.click();
                    }
                }
            });
            
            // Real-time system monitoring
            function updateSystemMetrics() {
                // In real implementation, fetch current system metrics
                console.log('Updating system metrics...');
            }
            
            // Update metrics every 30 seconds
            setInterval(updateSystemMetrics, 30000);
            
            // Warning for critical changes
            const criticalInputs = document.querySelectorAll('input[type="number"], input[type="range"]');
            criticalInputs.forEach(input => {
                input.addEventListener('change', function() {
                    const value = parseInt(this.value);
                    const label = this.closest('div').querySelector('label').textContent;
                    
                    // Warn for potentially dangerous settings
                    if (label.includes('Worker Processes') && value > 12) {
                        alert('Warning: High worker process count may impact system performance.');
                    }
                    
                    if (label.includes('Memory Limit') && value > 16) {
                        alert('Warning: High memory limits may cause resource contention.');
                    }
                    
                    if (label.includes('CPU Threshold') && value < 60) {
                        alert('Warning: Low CPU threshold may cause frequent scaling events.');
                    }
                });
            });
        });
    </script>


    </div>
  );
};

export default Untitled1;