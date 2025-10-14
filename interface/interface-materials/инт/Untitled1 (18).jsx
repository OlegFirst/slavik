import React from 'react';

const Untitled1 = () => {
  return (
    <div>
      
    
    <nav className="bg-white border-b border-gray-200 px-4 py-3 sm:px-6">
        <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-danger-600 rounded-lg flex items-center justify-center">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="shield-alert" className="lucide lucide-shield-alert w-6 h-6 text-white"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"></path><path d="M12 8v4"></path><path d="M12 16h.01"></path></svg>
                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-gray-900">AI-Platform-ISO Admin</h1>
                        <p className="text-xs text-gray-500">Service Monitoring</p>
                    </div>
                </div>
            </div>
            <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2 px-3 py-1 bg-success-100 text-success-800 rounded-full text-sm font-medium">
                    <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></div>
                    <span>21/23 Services Healthy</span>
                </div>
                <button className="relative p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bell" className="lucide lucide-bell w-5 h-5"><path d="M10.268 21a2 2 0 0 0 3.464 0"></path><path d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326"></path></svg>
                    <span className="absolute -top-1 -right-1 w-3 h-3 bg-warning-500 rounded-full flex items-center justify-center">
                        <span className="w-1.5 h-1.5 bg-white rounded-full"></span>
                    </span>
                </button>
                <div className="flex items-center space-x-3 pl-3 border-l border-gray-200">
                    <div className="w-8 h-8 bg-danger-100 rounded-full flex items-center justify-center">
                        <span className="text-sm font-medium text-danger-600">SA</span>
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
                        <a href="#" className="bg-danger-50 text-danger-700 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="server" className="lucide lucide-server text-danger-500 mr-3 h-5 w-5"><rect width="20" height="8" x="2" y="2" rx="2" ry="2"></rect><rect width="20" height="8" x="2" y="14" rx="2" ry="2"></rect><line x1="6" x2="6.01" y1="6" y2="6"></line><line x1="6" x2="6.01" y1="18" y2="18"></line></svg>
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
                        <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="cog" className="lucide lucide-cog text-gray-400 mr-3 h-5 w-5"><path d="M11 10.27 7 3.34"></path><path d="m11 13.73-4 6.93"></path><path d="M12 22v-2"></path><path d="M12 2v2"></path><path d="M14 12h8"></path><path d="m17 20.66-1-1.73"></path><path d="m17 3.34-1 1.73"></path><path d="M2 12h2"></path><path d="m20.66 17-1.73-1"></path><path d="m20.66 7-1.73 1"></path><path d="m3.34 17 1.73-1"></path><path d="m3.34 7 1.73 1"></path><circle cx="12" cy="12" r="2"></circle><circle cx="12" cy="12" r="8"></circle></svg>
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
                                <h1 className="text-2xl font-bold text-gray-900">Service Monitoring</h1>
                                <p className="mt-1 text-sm text-gray-500">Monitor and manage all platform services</p>
                            </div>
                            <div className="mt-4 sm:mt-0 flex space-x-3">
                                <button className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="refresh-cw" className="lucide lucide-refresh-cw w-4 h-4 mr-2"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"></path><path d="M21 3v5h-5"></path><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"></path><path d="M8 16H3v5"></path></svg>
                                    Refresh All
                                </button>
                                <button className="bg-warning-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-warning-700 transition-colors flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="pause" className="lucide lucide-pause w-4 h-4 mr-2"><rect x="14" y="3" width="5" height="18" rx="1"></rect><rect x="5" y="3" width="5" height="18" rx="1"></rect></svg>
                                    Stop All
                                </button>
                                <button className="bg-success-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-success-700 transition-colors flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="play" className="lucide lucide-play w-4 h-4 mr-2"><path d="M5 5a2 2 0 0 1 3.008-1.728l11.997 6.998a2 2 0 0 1 .003 3.458l-12 7A2 2 0 0 1 5 19z"></path></svg>
                                    Start All
                                </button>
                            </div>
                        </div>
                    </div>

                    
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Total Services</p>
                                    <p className="text-2xl font-bold text-gray-900">23</p>
                                    <p className="text-xs text-gray-500 mt-1">Platform + Intelligent Core</p>
                                </div>
                                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="server" className="lucide lucide-server w-6 h-6 text-blue-600"><rect width="20" height="8" x="2" y="2" rx="2" ry="2"></rect><rect width="20" height="8" x="2" y="14" rx="2" ry="2"></rect><line x1="6" x2="6.01" y1="6" y2="6"></line><line x1="6" x2="6.01" y1="18" y2="18"></line></svg>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Healthy</p>
                                    <p className="text-2xl font-bold text-success-600">21</p>
                                    <p className="text-xs text-success-600 mt-1">91.3% uptime</p>
                                </div>
                                <div className="w-12 h-12 bg-success-100 rounded-full flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check-circle" className="lucide lucide-check-circle w-6 h-6 text-success-600"><path d="M21.801 10A10 10 0 1 1 17 3.335"></path><path d="m9 11 3 3L22 4"></path></svg>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Degraded</p>
                                    <p className="text-2xl font-bold text-warning-600">1</p>
                                    <p className="text-xs text-warning-600 mt-1">High response time</p>
                                </div>
                                <div className="w-12 h-12 bg-warning-100 rounded-full flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="alert-triangle" className="lucide lucide-alert-triangle w-6 h-6 text-warning-600"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Down</p>
                                    <p className="text-2xl font-bold text-danger-600">1</p>
                                    <p className="text-xs text-danger-600 mt-1">Requires attention</p>
                                </div>
                                <div className="w-12 h-12 bg-danger-100 rounded-full flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="x-circle" className="lucide lucide-x-circle w-6 h-6 text-danger-600"><circle cx="12" cy="12" r="10"></circle><path d="m15 9-6 6"></path><path d="m9 9 6 6"></path></svg>
                                </div>
                            </div>
                        </div>
                    </div>

                    
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Service Category</label>
                                <select className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500 text-sm">
                                    <option value="">All Categories</option>
                                    <option value="platform">Platform Services (12)</option>
                                    <option value="intelligent">Intelligent Core (11)</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Health Status</label>
                                <select className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500 text-sm">
                                    <option value="">All Status</option>
                                    <option value="healthy">Healthy</option>
                                    <option value="degraded">Degraded</option>
                                    <option value="down">Down</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">Port Range</label>
                                <select className="block w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-primary-500 focus:border-primary-500 text-sm">
                                    <option value="">All Ports</option>
                                    <option value="8000-8099">8000-8099 (Platform)</option>
                                    <option value="9000-9099">9000-9099 (Intelligent)</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-2">View Mode</label>
                                <div className="flex items-center space-x-1 bg-gray-100 rounded-lg p-1">
                                    <button className="px-3 py-1 text-xs font-medium bg-white text-gray-900 rounded shadow-sm">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="grid-3x3" className="lucide lucide-grid-3x3 w-3 h-3"><rect width="18" height="18" x="3" y="3" rx="2"></rect><path d="M3 9h18"></path><path d="M3 15h18"></path><path d="M9 3v18"></path><path d="M15 3v18"></path></svg>
                                    </button>
                                    <button className="px-3 py-1 text-xs font-medium text-gray-500 hover:text-gray-700">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="list" className="lucide lucide-list w-3 h-3"><path d="M3 5h.01"></path><path d="M3 12h.01"></path><path d="M3 19h.01"></path><path d="M8 5h13"></path><path d="M8 12h13"></path><path d="M8 19h13"></path></svg>
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    
                    <div className="mb-8">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-lg font-semibold text-gray-900">Platform Services</h2>
                            <span className="text-sm text-gray-500">12 services</span>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                            
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
                                <div className="flex items-center justify-between mb-3">
                                    <div className="flex items-center space-x-2">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <h3 className="font-medium text-gray-900">API Gateway</h3>
                                    </div>
                                    <span className="text-xs text-gray-500">:8000</span>
                                </div>
                                <div className="space-y-2 mb-4">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">CPU:</span>
                                        <span className="text-gray-900">23%</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Memory:</span>
                                        <span className="text-gray-900">156MB</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Uptime:</span>
                                        <span className="text-gray-900">7d 12h</span>
                                    </div>
                                </div>
                                <div className="flex space-x-2">
                                    <button className="flex-1 px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors">
                                        Logs
                                    </button>
                                    <button className="flex-1 px-3 py-1 text-xs bg-warning-100 text-warning-700 rounded hover:bg-warning-200 transition-colors">
                                        Restart
                                    </button>
                                </div>
                            </div>

                            
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
                                <div className="flex items-center justify-between mb-3">
                                    <div className="flex items-center space-x-2">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <h3 className="font-medium text-gray-900">Auth Service</h3>
                                    </div>
                                    <span className="text-xs text-gray-500">:8001</span>
                                </div>
                                <div className="space-y-2 mb-4">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">CPU:</span>
                                        <span className="text-gray-900">12%</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Memory:</span>
                                        <span className="text-gray-900">89MB</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Uptime:</span>
                                        <span className="text-gray-900">7d 12h</span>
                                    </div>
                                </div>
                                <div className="flex space-x-2">
                                    <button className="flex-1 px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors">
                                        Logs
                                    </button>
                                    <button className="flex-1 px-3 py-1 text-xs bg-warning-100 text-warning-700 rounded hover:bg-warning-200 transition-colors">
                                        Restart
                                    </button>
                                </div>
                            </div>

                            
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
                                <div className="flex items-center justify-between mb-3">
                                    <div className="flex items-center space-x-2">
                                        <div className="w-3 h-3 bg-warning-500 rounded-full animate-pulse"></div>
                                        <h3 className="font-medium text-gray-900">User Service</h3>
                                    </div>
                                    <span className="text-xs text-gray-500">:8002</span>
                                </div>
                                <div className="space-y-2 mb-4">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">CPU:</span>
                                        <span className="text-warning-600">78%</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Memory:</span>
                                        <span className="text-gray-900">234MB</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Uptime:</span>
                                        <span className="text-gray-900">7d 12h</span>
                                    </div>
                                </div>
                                <div className="flex space-x-2">
                                    <button className="flex-1 px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors">
                                        Logs
                                    </button>
                                    <button className="flex-1 px-3 py-1 text-xs bg-warning-100 text-warning-700 rounded hover:bg-warning-200 transition-colors">
                                        Restart
                                    </button>
                                </div>
                            </div>

                            
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
                                <div className="flex items-center justify-between mb-3">
                                    <div className="flex items-center space-x-2">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <h3 className="font-medium text-gray-900">Organization Service</h3>
                                    </div>
                                    <span className="text-xs text-gray-500">:8003</span>
                                </div>
                                <div className="space-y-2 mb-4">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">CPU:</span>
                                        <span className="text-gray-900">15%</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Memory:</span>
                                        <span className="text-gray-900">67MB</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Uptime:</span>
                                        <span className="text-gray-900">7d 12h</span>
                                    </div>
                                </div>
                                <div className="flex space-x-2">
                                    <button className="flex-1 px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors">
                                        Logs
                                    </button>
                                    <button className="flex-1 px-3 py-1 text-xs bg-warning-100 text-warning-700 rounded hover:bg-warning-200 transition-colors">
                                        Restart
                                    </button>
                                </div>
                            </div>

                            
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
                                <div className="flex items-center justify-between mb-3">
                                    <div className="flex items-center space-x-2">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <h3 className="font-medium text-gray-900">BIA Service</h3>
                                    </div>
                                    <span className="text-xs text-gray-500">:8004</span>
                                </div>
                                <div className="space-y-2 mb-4">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">CPU:</span>
                                        <span className="text-gray-900">31%</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Memory:</span>
                                        <span className="text-gray-900">145MB</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Uptime:</span>
                                        <span className="text-gray-900">7d 12h</span>
                                    </div>
                                </div>
                                <div className="flex space-x-2">
                                    <button className="flex-1 px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors">
                                        Logs
                                    </button>
                                    <button className="flex-1 px-3 py-1 text-xs bg-warning-100 text-warning-700 rounded hover:bg-warning-200 transition-colors">
                                        Restart
                                    </button>
                                </div>
                            </div>

                            
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
                                <div className="flex items-center justify-between mb-3">
                                    <div className="flex items-center space-x-2">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <h3 className="font-medium text-gray-900">Risk Service</h3>
                                    </div>
                                    <span className="text-xs text-gray-500">:8005</span>
                                </div>
                                <div className="space-y-2 mb-4">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">CPU:</span>
                                        <span className="text-gray-900">19%</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Memory:</span>
                                        <span className="text-gray-900">98MB</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Uptime:</span>
                                        <span className="text-gray-900">7d 12h</span>
                                    </div>
                                </div>
                                <div className="flex space-x-2">
                                    <button className="flex-1 px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors">
                                        Logs
                                    </button>
                                    <button className="flex-1 px-3 py-1 text-xs bg-warning-100 text-warning-700 rounded hover:bg-warning-200 transition-colors">
                                        Restart
                                    </button>
                                </div>
                            </div>

                            
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
                                <div className="flex items-center justify-between mb-3">
                                    <div className="flex items-center space-x-2">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <h3 className="font-medium text-gray-900">Plan Service</h3>
                                    </div>
                                    <span className="text-xs text-gray-500">:8006</span>
                                </div>
                                <div className="space-y-2 mb-4">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">CPU:</span>
                                        <span className="text-gray-900">27%</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Memory:</span>
                                        <span className="text-gray-900">112MB</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Uptime:</span>
                                        <span className="text-gray-900">7d 12h</span>
                                    </div>
                                </div>
                                <div className="flex space-x-2">
                                    <button className="flex-1 px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors">
                                        Logs
                                    </button>
                                    <button className="flex-1 px-3 py-1 text-xs bg-warning-100 text-warning-700 rounded hover:bg-warning-200 transition-colors">
                                        Restart
                                    </button>
                                </div>
                            </div>

                            
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
                                <div className="flex items-center justify-between mb-3">
                                    <div className="flex items-center space-x-2">
                                        <div className="w-3 h-3 bg-danger-500 rounded-full"></div>
                                        <h3 className="font-medium text-gray-900">Exercise Service</h3>
                                    </div>
                                    <span className="text-xs text-gray-500">:8007</span>
                                </div>
                                <div className="space-y-2 mb-4">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">CPU:</span>
                                        <span className="text-danger-600">--</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Memory:</span>
                                        <span className="text-danger-600">--</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Uptime:</span>
                                        <span className="text-danger-600">Down</span>
                                    </div>
                                </div>
                                <div className="flex space-x-2">
                                    <button className="flex-1 px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors">
                                        Logs
                                    </button>
                                    <button className="flex-1 px-3 py-1 text-xs bg-success-100 text-success-700 rounded hover:bg-success-200 transition-colors">
                                        Start
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    
                    <div className="mb-8">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-lg font-semibold text-gray-900">Intelligent Core Services</h2>
                            <span className="text-sm text-gray-500">11 services</span>
                        </div>
                        
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                            
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
                                <div className="flex items-center justify-between mb-3">
                                    <div className="flex items-center space-x-2">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <h3 className="font-medium text-gray-900">AI Orchestrator</h3>
                                    </div>
                                    <span className="text-xs text-gray-500">:9000</span>
                                </div>
                                <div className="space-y-2 mb-4">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">CPU:</span>
                                        <span className="text-gray-900">45%</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Memory:</span>
                                        <span className="text-gray-900">512MB</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Uptime:</span>
                                        <span className="text-gray-900">7d 12h</span>
                                    </div>
                                </div>
                                <div className="flex space-x-2">
                                    <button className="flex-1 px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors">
                                        Logs
                                    </button>
                                    <button className="flex-1 px-3 py-1 text-xs bg-warning-100 text-warning-700 rounded hover:bg-warning-200 transition-colors">
                                        Restart
                                    </button>
                                </div>
                            </div>

                            
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
                                <div className="flex items-center justify-between mb-3">
                                    <div className="flex items-center space-x-2">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <h3 className="font-medium text-gray-900">LLM Gateway</h3>
                                    </div>
                                    <span className="text-xs text-gray-500">:9001</span>
                                </div>
                                <div className="space-y-2 mb-4">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">CPU:</span>
                                        <span className="text-gray-900">67%</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Memory:</span>
                                        <span className="text-gray-900">1.2GB</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Uptime:</span>
                                        <span className="text-gray-900">7d 12h</span>
                                    </div>
                                </div>
                                <div className="flex space-x-2">
                                    <button className="flex-1 px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors">
                                        Logs
                                    </button>
                                    <button className="flex-1 px-3 py-1 text-xs bg-warning-100 text-warning-700 rounded hover:bg-warning-200 transition-colors">
                                        Restart
                                    </button>
                                </div>
                            </div>

                            
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
                                <div className="flex items-center justify-between mb-3">
                                    <div className="flex items-center space-x-2">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <h3 className="font-medium text-gray-900">RAG Engine</h3>
                                    </div>
                                    <span className="text-xs text-gray-500">:9002</span>
                                </div>
                                <div className="space-y-2 mb-4">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">CPU:</span>
                                        <span className="text-gray-900">34%</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Memory:</span>
                                        <span className="text-gray-900">768MB</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Uptime:</span>
                                        <span className="text-gray-900">7d 12h</span>
                                    </div>
                                </div>
                                <div className="flex space-x-2">
                                    <button className="flex-1 px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors">
                                        Logs
                                    </button>
                                    <button className="flex-1 px-3 py-1 text-xs bg-warning-100 text-warning-700 rounded hover:bg-warning-200 transition-colors">
                                        Restart
                                    </button>
                                </div>
                            </div>

                            
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 hover:shadow-md transition-shadow">
                                <div className="flex items-center justify-between mb-3">
                                    <div className="flex items-center space-x-2">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <h3 className="font-medium text-gray-900">Vector Store</h3>
                                    </div>
                                    <span className="text-xs text-gray-500">:9003</span>
                                </div>
                                <div className="space-y-2 mb-4">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">CPU:</span>
                                        <span className="text-gray-900">28%</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Memory:</span>
                                        <span className="text-gray-900">2.1GB</span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-600">Uptime:</span>
                                        <span className="text-gray-900">7d 12h</span>
                                    </div>
                                </div>
                                <div className="flex space-x-2">
                                    <button className="flex-1 px-3 py-1 text-xs bg-gray-100 text-gray-700 rounded hover:bg-gray-200 transition-colors">
                                        Logs
                                    </button>
                                    <button className="flex-1 px-3 py-1 text-xs bg-warning-100 text-warning-700 rounded hover:bg-warning-200 transition-colors">
                                        Restart
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                        <div className="px-6 py-4 border-b border-gray-200">
                            <h3 className="text-lg font-semibold text-gray-900">Recent Alerts</h3>
                        </div>
                        <div className="divide-y divide-gray-200">
                            <div className="px-6 py-4 flex items-center justify-between">
                                <div className="flex items-center space-x-3">
                                    <div className="w-2 h-2 bg-danger-500 rounded-full"></div>
                                    <div>
                                        <p className="text-sm font-medium text-gray-900">Exercise Service is down</p>
                                        <p className="text-xs text-gray-500">Service stopped responding at port 8007</p>
                                    </div>
                                </div>
                                <div className="flex items-center space-x-2">
                                    <span className="text-xs text-gray-500">2 min ago</span>
                                    <button className="text-xs text-primary-600 hover:text-primary-700 font-medium">Investigate</button>
                                </div>
                            </div>
                            
                            <div className="px-6 py-4 flex items-center justify-between">
                                <div className="flex items-center space-x-3">
                                    <div className="w-2 h-2 bg-warning-500 rounded-full"></div>
                                    <div>
                                        <p className="text-sm font-medium text-gray-900">High CPU usage on User Service</p>
                                        <p className="text-xs text-gray-500">CPU usage at 78% for the last 15 minutes</p>
                                    </div>
                                </div>
                                <div className="flex items-center space-x-2">
                                    <span className="text-xs text-gray-500">15 min ago</span>
                                    <button className="text-xs text-primary-600 hover:text-primary-700 font-medium">View Metrics</button>
                                </div>
                            </div>
                            
                            <div className="px-6 py-4 flex items-center justify-between">
                                <div className="flex items-center space-x-3">
                                    <div className="w-2 h-2 bg-success-500 rounded-full"></div>
                                    <div>
                                        <p className="text-sm font-medium text-gray-900">All services restarted successfully</p>
                                        <p className="text-xs text-gray-500">Scheduled maintenance completed</p>
                                    </div>
                                </div>
                                <div className="flex items-center space-x-2">
                                    <span className="text-xs text-gray-500">2 hours ago</span>
                                    <button className="text-xs text-primary-600 hover:text-primary-700 font-medium">Details</button>
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
            <button className="flex flex-col items-center py-2 px-1 text-danger-600 bg-danger-50 rounded-lg">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="server" className="lucide lucide-server w-5 h-5"><rect width="20" height="8" x="2" y="2" rx="2" ry="2"></rect><rect width="20" height="8" x="2" y="14" rx="2" ry="2"></rect><line x1="6" x2="6.01" y1="6" y2="6"></line><line x1="6" x2="6.01" y1="18" y2="18"></line></svg>
                <span className="text-xs mt-1 font-medium">Services</span>
            </button>
            <button className="flex flex-col items-center py-2 px-1 text-gray-400 hover:text-gray-600">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="settings" className="lucide lucide-settings w-5 h-5"><path d="M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915"></path><circle cx="12" cy="12" r="3"></circle></svg>
                <span className="text-xs mt-1">Config</span>
            </button>
            <button className="flex flex-col items-center py-2 px-1 text-gray-400 hover:text-gray-600">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="file-text" className="lucide lucide-file-text w-5 h-5"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"></path><path d="M14 2v4a2 2 0 0 0 2 2h4"></path><path d="M10 9H8"></path><path d="M16 13H8"></path><path d="M16 17H8"></path></svg>
                <span className="text-xs mt-1">Logs</span>
            </button>
        </div>
    </div>

    <script>
        // Initialize Lucide icons
        lucide.createIcons();
        
        document.addEventListener('DOMContentLoaded', function() {
            // Service action buttons
            const logButtons = document.querySelectorAll('button:contains("Logs")');
            const restartButtons = document.querySelectorAll('button:contains("Restart")');
            const startButtons = document.querySelectorAll('button:contains("Start")');

            // Logs buttons
            document.querySelectorAll('button').forEach(btn => {
                if (btn.textContent.trim() === 'Logs') {
                    btn.addEventListener('click', function() {
                        const serviceCard = this.closest('.bg-white');
                        const serviceName = serviceCard.querySelector('h3').textContent;
                        console.log('View logs for:', serviceName);
                        // Open logs modal or navigate to logs page
                    });
                }
            });

            // Restart buttons
            document.querySelectorAll('button').forEach(btn => {
                if (btn.textContent.trim() === 'Restart') {
                    btn.addEventListener('click', function() {
                        const serviceCard = this.closest('.bg-white');
                        const serviceName = serviceCard.querySelector('h3').textContent;
                        console.log('Restart service:', serviceName);
                        
                        // Show confirmation dialog
                        if (confirm(`Are you sure you want to restart ${serviceName}?`)) {
                            // Simulate restart process
                            this.textContent = 'Restarting...';
                            this.disabled = true;
                            
                            setTimeout(() => {
                                this.textContent = 'Restart';
                                this.disabled = false;
                                console.log(`${serviceName} restarted successfully`);
                            }, 3000);
                        }
                    });
                }
            });

            // Start buttons (for down services)
            document.querySelectorAll('button').forEach(btn => {
                if (btn.textContent.trim() === 'Start') {
                    btn.addEventListener('click', function() {
                        const serviceCard = this.closest('.bg-white');
                        const serviceName = serviceCard.querySelector('h3').textContent;
                        console.log('Start service:', serviceName);
                        
                        // Simulate start process
                        this.textContent = 'Starting...';
                        this.disabled = true;
                        
                        setTimeout(() => {
                            // Update service status to healthy
                            const statusDot = serviceCard.querySelector('.w-3.h-3');
                            statusDot.className = 'w-3 h-3 bg-success-500 rounded-full';
                            
                            // Update metrics
                            const cpuSpan = serviceCard.querySelector('.text-danger-600');
                            if (cpuSpan && cpuSpan.textContent === '--') {
                                cpuSpan.textContent = '15%';
                                cpuSpan.className = 'text-gray-900';
                            }
                            
                            this.textContent = 'Restart';
                            this.className = 'flex-1 px-3 py-1 text-xs bg-warning-100 text-warning-700 rounded hover:bg-warning-200 transition-colors';
                            this.disabled = false;
                            
                            console.log(`${serviceName} started successfully`);
                        }, 2000);
                    });
                }
            });

            // Global action buttons
            const refreshAllBtn = document.querySelector('button:has(i[data-lucide="refresh-cw"])');
            const stopAllBtn = document.querySelector('button:has(i[data-lucide="pause"])');
            const startAllBtn = document.querySelector('button:has(i[data-lucide="play"])');

            if (refreshAllBtn) {
                refreshAllBtn.addEventListener('click', function() {
                    console.log('Refreshing all services...');
                    const icon = this.querySelector('i');
                    icon.classList.add('animate-spin');
                    
                    setTimeout(() => {
                        icon.classList.remove('animate-spin');
                        console.log('All services refreshed');
                    }, 2000);
                });
            }

            if (stopAllBtn) {
                stopAllBtn.addEventListener('click', function() {
                    if (confirm('Are you sure you want to stop all services? This will make the platform unavailable.')) {
                        console.log('Stopping all services...');
                        // Implement stop all logic
                    }
                });
            }

            if (startAllBtn) {
                startAllBtn.addEventListener('click', function() {
                    console.log('Starting all services...');
                    // Implement start all logic
                });
            }

            // Filter functionality
            const filterSelects = document.querySelectorAll('select');
            filterSelects.forEach(select => {
                select.addEventListener('change', function() {
                    const filterType = this.previousElementSibling.textContent;
                    const filterValue = this.value;
                    console.log(`Filter ${filterType}:`, filterValue);
                    // Implement filtering logic
                });
            });

            // View mode toggle
            const viewModeButtons = document.querySelectorAll('.bg-gray-100 button');
            viewModeButtons.forEach(btn => {
                btn.addEventListener('click', function() {
                    // Remove active state from all buttons
                    viewModeButtons.forEach(b => {
                        b.classList.remove('bg-white', 'text-gray-900', 'shadow-sm');
                        b.classList.add('text-gray-500');
                    });
                    
                    // Add active state to clicked button
                    this.classList.add('bg-white', 'text-gray-900', 'shadow-sm');
                    this.classList.remove('text-gray-500');
                    
                    const viewMode = this.querySelector('i').getAttribute('data-lucide');
                    console.log('View mode changed to:', viewMode);
                    
                    // Toggle between grid and list view
                    const serviceGrids = document.querySelectorAll('.grid.grid-cols-1.md\\:grid-cols-2');
                    if (viewMode === 'list') {
                        // Switch to list view
                        serviceGrids.forEach(grid => {
                            grid.className = 'space-y-2';
                        });
                    } else {
                        // Switch to grid view
                        serviceGrids.forEach(grid => {
                            grid.className = 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4';
                        });
                    }
                });
            });

            // Alert action buttons
            const alertButtons = document.querySelectorAll('button:contains("Investigate"), button:contains("View Metrics"), button:contains("Details")');
            document.querySelectorAll('button').forEach(btn => {
                const text = btn.textContent.trim();
                if (['Investigate', 'View Metrics', 'Details'].includes(text)) {
                    btn.addEventListener('click', function() {
                        const alertRow = this.closest('.px-6');
                        const alertTitle = alertRow.querySelector('.font-medium').textContent;
                        console.log(`${text} alert:`, alertTitle);
                        // Handle alert action
                    });
                }
            });

            // Real-time updates simulation
            function updateMetrics() {
                // Simulate real-time metric updates
                const cpuElements = document.querySelectorAll('.text-gray-900, .text-warning-600');
                cpuElements.forEach(element => {
                    if (element.textContent.includes('%') && !element.textContent.includes('--')) {
                        const currentValue = parseInt(element.textContent);
                        const newValue = Math.max(5, Math.min(95, currentValue + Math.floor(Math.random() * 10 - 5)));
                        element.textContent = newValue + '%';
                        
                        // Update color based on value
                        if (newValue > 70) {
                            element.className = 'text-warning-600';
                        } else {
                            element.className = 'text-gray-900';
                        }
                    }
                });
            }

            // Update metrics every 30 seconds
            setInterval(updateMetrics, 30000);

            // Simulate new alerts
            function addNewAlert() {
                const alerts = [
                    {
                        type: 'warning',
                        title: 'Memory usage spike detected',
                        description: 'LLM Gateway memory usage increased to 1.8GB',
                        time: 'Just now'
                    },
                    {
                        type: 'success',
                        title: 'Service auto-recovery successful',
                        description: 'User Service CPU usage normalized',
                        time: 'Just now'
                    }
                ];
                
                // Randomly add new alerts (for demo purposes)
                if (Math.random() < 0.1) { // 10% chance every interval
                    const alert = alerts[Math.floor(Math.random() * alerts.length)];
                    console.log('New alert:', alert.title);
                    // In real implementation, this would update the alerts section
                }
            }

            // Check for new alerts every minute
            setInterval(addNewAlert, 60000);
        });
    </script>


    </div>
  );
};

export default Untitled1;