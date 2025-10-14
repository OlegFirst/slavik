import React from 'react';

const Untitled1 = () => {
  return (
    <div>
      
    
    <nav className="bg-white border-b border-gray-200 px-4 py-3 sm:px-6">
        <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="cpu" className="lucide lucide-cpu w-6 h-6 text-white"><path d="M12 20v2"></path><path d="M12 2v2"></path><path d="M17 20v2"></path><path d="M17 2v2"></path><path d="M2 12h2"></path><path d="M2 17h2"></path><path d="M2 7h2"></path><path d="M20 12h2"></path><path d="M20 17h2"></path><path d="M20 7h2"></path><path d="M7 20v2"></path><path d="M7 2v2"></path><rect x="4" y="4" width="16" height="16" rx="2"></rect><rect x="8" y="8" width="8" height="8" rx="1"></rect></svg>
                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-gray-900">AI-Platform-ISO Admin</h1>
                        <p className="text-xs text-gray-500">Infrastructure Monitoring</p>
                    </div>
                </div>
            </div>
            <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2 px-3 py-1 bg-success-100 text-success-800 rounded-full text-sm font-medium">
                    <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></div>
                    <span>All Systems Operational</span>
                </div>
                <button className="relative p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bell" className="lucide lucide-bell w-5 h-5"><path d="M10.268 21a2 2 0 0 0 3.464 0"></path><path d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326"></path></svg>
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
                        <a href="#" className="bg-primary-50 text-primary-700 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="cpu" className="lucide lucide-cpu text-primary-500 mr-3 h-5 w-5"><path d="M12 20v2"></path><path d="M12 2v2"></path><path d="M17 20v2"></path><path d="M17 2v2"></path><path d="M2 12h2"></path><path d="M2 17h2"></path><path d="M2 7h2"></path><path d="M20 12h2"></path><path d="M20 17h2"></path><path d="M20 7h2"></path><path d="M7 20v2"></path><path d="M7 2v2"></path><rect x="4" y="4" width="16" height="16" rx="2"></rect><rect x="8" y="8" width="8" height="8" rx="1"></rect></svg>
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
                                <h1 className="text-2xl font-bold text-gray-900">Infrastructure Monitoring</h1>
                                <p className="mt-1 text-sm text-gray-500">Monitor databases, message queues, and core infrastructure components</p>
                            </div>
                            <div className="mt-4 sm:mt-0 flex space-x-3">
                                <button className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="refresh-cw" className="lucide lucide-refresh-cw w-4 h-4 mr-2"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"></path><path d="M21 3v5h-5"></path><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"></path><path d="M8 16H3v5"></path></svg>
                                    Refresh All
                                </button>
                                <button className="bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="download" className="lucide lucide-download w-4 h-4 mr-2"><path d="M12 15V3"></path><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><path d="m7 10 5 5 5-5"></path></svg>
                                    Export Report
                                </button>
                            </div>
                        </div>
                    </div>

                    
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Components</p>
                                    <p className="text-2xl font-bold text-gray-900">7</p>
                                    <p className="text-xs text-gray-500 mt-1">Core infrastructure</p>
                                </div>
                                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="layers" className="lucide lucide-layers w-6 h-6 text-blue-600"><path d="M12.83 2.18a2 2 0 0 0-1.66 0L2.6 6.08a1 1 0 0 0 0 1.83l8.58 3.91a2 2 0 0 0 1.66 0l8.58-3.9a1 1 0 0 0 0-1.83z"></path><path d="M2 12a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 12"></path><path d="M2 17a1 1 0 0 0 .58.91l8.6 3.91a2 2 0 0 0 1.65 0l8.58-3.9A1 1 0 0 0 22 17"></path></svg>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Healthy</p>
                                    <p className="text-2xl font-bold text-success-600">7</p>
                                    <p className="text-xs text-success-600 mt-1">100% operational</p>
                                </div>
                                <div className="w-12 h-12 bg-success-100 rounded-full flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check-circle" className="lucide lucide-check-circle w-6 h-6 text-success-600"><path d="M21.801 10A10 10 0 1 1 17 3.335"></path><path d="m9 11 3 3L22 4"></path></svg>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Total Storage</p>
                                    <p className="text-2xl font-bold text-gray-900">2.4TB</p>
                                    <p className="text-xs text-gray-500 mt-1">67% utilized</p>
                                </div>
                                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="hard-drive" className="lucide lucide-hard-drive w-6 h-6 text-purple-600"><line x1="22" x2="2" y1="12" y2="12"></line><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"></path><line x1="6" x2="6.01" y1="16" y2="16"></line><line x1="10" x2="10.01" y1="16" y2="16"></line></svg>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Avg Response</p>
                                    <p className="text-2xl font-bold text-gray-900">12ms</p>
                                    <p className="text-xs text-success-600 mt-1">Excellent performance</p>
                                </div>
                                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="zap" className="lucide lucide-zap w-6 h-6 text-green-600"><path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"></path></svg>
                                </div>
                            </div>
                        </div>
                    </div>

                    
                    <div className="mb-8">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-lg font-semibold text-gray-900">Database Systems</h2>
                            <span className="text-sm text-gray-500">2 databases</span>
                        </div>
                        
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="database" className="lucide lucide-database w-6 h-6 text-blue-600"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M3 5V19A9 3 0 0 0 21 19V5"></path><path d="M3 12A9 3 0 0 0 21 12"></path></svg>
                                        </div>
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-900">PostgreSQL</h3>
                                            <p className="text-sm text-gray-500">Primary Database</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <span className="text-sm font-medium text-success-600">Healthy</span>
                                    </div>
                                </div>
                                
                                <div className="grid grid-cols-2 gap-4 mb-4">
                                    <div className="bg-gray-50 rounded-lg p-3">
                                        <p className="text-xs text-gray-600 mb-1">Connections</p>
                                        <p className="text-lg font-semibold text-gray-900">47/200</p>
                                        <div className="w-full bg-gray-200 rounded-full h-1.5 mt-2">
                                            <div className="bg-success-500 h-1.5 rounded-full" style={{width: '23.5%'}}></div>
                                        </div>
                                    </div>
                                    <div className="bg-gray-50 rounded-lg p-3">
                                        <p className="text-xs text-gray-600 mb-1">Database Size</p>
                                        <p className="text-lg font-semibold text-gray-900">1.2GB</p>
                                        <p className="text-xs text-success-600 mt-1">+12MB today</p>
                                    </div>
                                    <div className="bg-gray-50 rounded-lg p-3">
                                        <p className="text-xs text-gray-600 mb-1">Queries/sec</p>
                                        <p className="text-lg font-semibold text-gray-900">234</p>
                                        <p className="text-xs text-gray-500 mt-1">Avg response: 8ms</p>
                                    </div>
                                    <div className="bg-gray-50 rounded-lg p-3">
                                        <p className="text-xs text-gray-600 mb-1">Slow Queries</p>
                                        <p className="text-lg font-semibold text-gray-900">3</p>
                                        <p className="text-xs text-warning-600 mt-1">Last hour</p>
                                    </div>
                                </div>
                                
                                <div className="flex space-x-2">
                                    <button className="flex-1 px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
                                        View Queries
                                    </button>
                                    <button className="flex-1 px-3 py-2 text-sm bg-primary-100 text-primary-700 rounded-lg hover:bg-primary-200 transition-colors">
                                        Backup Now
                                    </button>
                                    <button className="px-3 py-2 text-sm bg-warning-100 text-warning-700 rounded-lg hover:bg-warning-200 transition-colors">
                                        Optimize
                                    </button>
                                </div>
                            </div>

                            
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="brain" className="lucide lucide-brain w-6 h-6 text-purple-600"><path d="M12 18V5"></path><path d="M15 13a4.17 4.17 0 0 1-3-4 4.17 4.17 0 0 1-3 4"></path><path d="M17.598 6.5A3 3 0 1 0 12 5a3 3 0 1 0-5.598 1.5"></path><path d="M17.997 5.125a4 4 0 0 1 2.526 5.77"></path><path d="M18 18a4 4 0 0 0 2-7.464"></path><path d="M19.967 17.483A4 4 0 1 1 12 18a4 4 0 1 1-7.967-.517"></path><path d="M6 18a4 4 0 0 1-2-7.464"></path><path d="M6.003 5.125a4 4 0 0 0-2.526 5.77"></path></svg>
                                        </div>
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-900">Qdrant</h3>
                                            <p className="text-sm text-gray-500">Vector Database</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <span className="text-sm font-medium text-success-600">Healthy</span>
                                    </div>
                                </div>
                                
                                <div className="grid grid-cols-2 gap-4 mb-4">
                                    <div className="bg-gray-50 rounded-lg p-3">
                                        <p className="text-xs text-gray-600 mb-1">Collections</p>
                                        <p className="text-lg font-semibold text-gray-900">12</p>
                                        <p className="text-xs text-gray-500 mt-1">Active collections</p>
                                    </div>
                                    <div className="bg-gray-50 rounded-lg p-3">
                                        <p className="text-xs text-gray-600 mb-1">Total Vectors</p>
                                        <p className="text-lg font-semibold text-gray-900">2.4M</p>
                                        <p className="text-xs text-success-600 mt-1">+1.2K today</p>
                                    </div>
                                    <div className="bg-gray-50 rounded-lg p-3">
                                        <p className="text-xs text-gray-600 mb-1">Search Latency</p>
                                        <p className="text-lg font-semibold text-gray-900">15ms</p>
                                        <p className="text-xs text-success-600 mt-1">Excellent</p>
                                    </div>
                                    <div className="bg-gray-50 rounded-lg p-3">
                                        <p className="text-xs text-gray-600 mb-1">Memory Usage</p>
                                        <p className="text-lg font-semibold text-gray-900">3.2GB</p>
                                        <p className="text-xs text-gray-500 mt-1">of 8GB allocated</p>
                                    </div>
                                </div>
                                
                                <div className="flex space-x-2">
                                    <button className="flex-1 px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
                                        View Collections
                                    </button>
                                    <button className="flex-1 px-3 py-2 text-sm bg-purple-100 text-purple-700 rounded-lg hover:bg-purple-200 transition-colors">
                                        Reindex
                                    </button>
                                    <button className="px-3 py-2 text-sm bg-warning-100 text-warning-700 rounded-lg hover:bg-warning-200 transition-colors">
                                        Optimize
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    
                    <div className="mb-8">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-lg font-semibold text-gray-900">Message Queue &amp; Cache</h2>
                            <span className="text-sm text-gray-500">2 systems</span>
                        </div>
                        
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="shuffle" className="lucide lucide-shuffle w-6 h-6 text-orange-600"><path d="m18 14 4 4-4 4"></path><path d="m18 2 4 4-4 4"></path><path d="M2 18h1.973a4 4 0 0 0 3.3-1.7l5.454-8.6a4 4 0 0 1 3.3-1.7H22"></path><path d="M2 6h1.972a4 4 0 0 1 3.6 2.2"></path><path d="M22 18h-6.041a4 4 0 0 1-3.3-1.8l-.359-.45"></path></svg>
                                        </div>
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-900">RabbitMQ</h3>
                                            <p className="text-sm text-gray-500">Message Queue</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <span className="text-sm font-medium text-success-600">Healthy</span>
                                    </div>
                                </div>
                                
                                <div className="grid grid-cols-2 gap-4 mb-4">
                                    <div className="bg-gray-50 rounded-lg p-3">
                                        <p className="text-xs text-gray-600 mb-1">Queues</p>
                                        <p className="text-lg font-semibold text-gray-900">23</p>
                                        <p className="text-xs text-gray-500 mt-1">Active queues</p>
                                    </div>
                                    <div className="bg-gray-50 rounded-lg p-3">
                                        <p className="text-xs text-gray-600 mb-1">Messages Ready</p>
                                        <p className="text-lg font-semibold text-gray-900">156</p>
                                        <p className="text-xs text-gray-500 mt-1">Pending processing</p>
                                    </div>
                                    <div className="bg-gray-50 rounded-lg p-3">
                                        <p className="text-xs text-gray-600 mb-1">Connections</p>
                                        <p className="text-lg font-semibold text-gray-900">12</p>
                                        <p className="text-xs text-success-600 mt-1">All healthy</p>
                                    </div>
                                    <div className="bg-gray-50 rounded-lg p-3">
                                        <p className="text-xs text-gray-600 mb-1">Throughput</p>
                                        <p className="text-lg font-semibold text-gray-900">1.2K/s</p>
                                        <p className="text-xs text-gray-500 mt-1">Messages/sec</p>
                                    </div>
                                </div>
                                
                                <div className="flex space-x-2">
                                    <button className="flex-1 px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
                                        View Queues
                                    </button>
                                    <button className="flex-1 px-3 py-2 text-sm bg-orange-100 text-orange-700 rounded-lg hover:bg-orange-200 transition-colors">
                                        Purge Queue
                                    </button>
                                </div>
                            </div>

                            
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="zap" className="lucide lucide-zap w-6 h-6 text-red-600"><path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"></path></svg>
                                        </div>
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-900">Redis</h3>
                                            <p className="text-sm text-gray-500">Cache &amp; Session Store</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <span className="text-sm font-medium text-success-600">Healthy</span>
                                    </div>
                                </div>
                                
                                <div className="grid grid-cols-2 gap-4 mb-4">
                                    <div className="bg-gray-50 rounded-lg p-3">
                                        <p className="text-xs text-gray-600 mb-1">Memory Usage</p>
                                        <p className="text-lg font-semibold text-gray-900">245MB</p>
                                        <div className="w-full bg-gray-200 rounded-full h-1.5 mt-2">
                                            <div className="bg-success-500 h-1.5 rounded-full" style={{width: '24.5%'}}></div>
                                        </div>
                                    </div>
                                    <div className="bg-gray-50 rounded-lg p-3">
                                        <p className="text-xs text-gray-600 mb-1">Keys Count</p>
                                        <p className="text-lg font-semibold text-gray-900">12.4K</p>
                                        <p className="text-xs text-gray-500 mt-1">Active keys</p>
                                    </div>
                                    <div className="bg-gray-50 rounded-lg p-3">
                                        <p className="text-xs text-gray-600 mb-1">Hit Rate</p>
                                        <p className="text-lg font-semibold text-gray-900">94.2%</p>
                                        <p className="text-xs text-success-600 mt-1">Excellent</p>
                                    </div>
                                    <div className="bg-gray-50 rounded-lg p-3">
                                        <p className="text-xs text-gray-600 mb-1">Operations/sec</p>
                                        <p className="text-lg font-semibold text-gray-900">2.1K</p>
                                        <p className="text-xs text-gray-500 mt-1">Read/Write ops</p>
                                    </div>
                                </div>
                                
                                <div className="flex space-x-2">
                                    <button className="flex-1 px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
                                        View Keys
                                    </button>
                                    <button className="flex-1 px-3 py-2 text-sm bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors">
                                        Flush Cache
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    
                    <div className="mb-8">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-lg font-semibold text-gray-900">Monitoring &amp; Events</h2>
                            <span className="text-sm text-gray-500">3 systems</span>
                        </div>
                        
                        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                            
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-10 h-10 bg-indigo-100 rounded-lg flex items-center justify-center">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="radio" className="lucide lucide-radio w-6 h-6 text-indigo-600"><path d="M16.247 7.761a6 6 0 0 1 0 8.478"></path><path d="M19.075 4.933a10 10 0 0 1 0 14.134"></path><path d="M4.925 19.067a10 10 0 0 1 0-14.134"></path><path d="M7.753 16.239a6 6 0 0 1 0-8.478"></path><circle cx="12" cy="12" r="2"></circle></svg>
                                        </div>
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-900">EventBus</h3>
                                            <p className="text-sm text-gray-500">Event Streaming</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <span className="text-sm font-medium text-success-600">Healthy</span>
                                    </div>
                                </div>
                                
                                <div className="space-y-3 mb-4">
                                    <div className="bg-gray-50 rounded-lg p-3">
                                        <p className="text-xs text-gray-600 mb-1">Events Today</p>
                                        <p className="text-lg font-semibold text-gray-900">45.2K</p>
                                    </div>
                                    <div className="bg-gray-50 rounded-lg p-3">
                                        <p className="text-xs text-gray-600 mb-1">Dead Letter Queue</p>
                                        <p className="text-lg font-semibold text-gray-900">0</p>
                                    </div>
                                </div>
                                
                                <div className="flex space-x-2">
                                    <button className="flex-1 px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
                                        View Events
                                    </button>
                                </div>
                            </div>

                            
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="activity" className="lucide lucide-activity w-6 h-6 text-yellow-600"><path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2"></path></svg>
                                        </div>
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-900">Prometheus</h3>
                                            <p className="text-sm text-gray-500">Metrics Collection</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <span className="text-sm font-medium text-success-600">Healthy</span>
                                    </div>
                                </div>
                                
                                <div className="space-y-3 mb-4">
                                    <div className="bg-gray-50 rounded-lg p-3">
                                        <p className="text-xs text-gray-600 mb-1">Metrics Scraped</p>
                                        <p className="text-lg font-semibold text-gray-900">1.2M</p>
                                    </div>
                                    <div className="bg-gray-50 rounded-lg p-3">
                                        <p className="text-xs text-gray-600 mb-1">Active Alerts</p>
                                        <p className="text-lg font-semibold text-gray-900">0</p>
                                    </div>
                                </div>
                                
                                <div className="flex space-x-2">
                                    <button className="flex-1 px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors">
                                        View Metrics
                                    </button>
                                </div>
                            </div>

                            
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bar-chart-3" className="lucide lucide-bar-chart-3 w-6 h-6 text-green-600"><path d="M3 3v16a2 2 0 0 0 2 2h16"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>
                                        </div>
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-900">Grafana</h3>
                                            <p className="text-sm text-gray-500">Visualization</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <span className="text-sm font-medium text-success-600">Healthy</span>
                                    </div>
                                </div>
                                
                                <div className="space-y-3 mb-4">
                                    <div className="bg-gray-50 rounded-lg p-3">
                                        <p className="text-xs text-gray-600 mb-1">Dashboards</p>
                                        <p className="text-lg font-semibold text-gray-900">15</p>
                                    </div>
                                    <div className="bg-gray-50 rounded-lg p-3">
                                        <p className="text-xs text-gray-600 mb-1">Active Users</p>
                                        <p className="text-lg font-semibold text-gray-900">8</p>
                                    </div>
                                </div>
                                
                                <div className="flex space-x-2">
                                    <button className="flex-1 px-3 py-2 text-sm bg-green-100 text-green-700 rounded-lg hover:bg-green-200 transition-colors">
                                        Open Grafana
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                        <div className="px-6 py-4 border-b border-gray-200">
                            <h3 className="text-lg font-semibold text-gray-900">Infrastructure Alerts</h3>
                        </div>
                        <div className="p-6">
                            <div className="text-center py-8">
                                <div className="w-16 h-16 bg-success-100 rounded-full flex items-center justify-center mx-auto mb-4">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check-circle" className="lucide lucide-check-circle w-8 h-8 text-success-600"><path d="M21.801 10A10 10 0 1 1 17 3.335"></path><path d="m9 11 3 3L22 4"></path></svg>
                                </div>
                                <h4 className="text-lg font-medium text-gray-900 mb-2">All Systems Operational</h4>
                                <p className="text-gray-500">No infrastructure alerts at this time. All components are running smoothly.</p>
                                <div className="mt-4 text-sm text-gray-400">
                                    Last check: <span className="font-medium">2 minutes ago</span>
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
            <button className="flex flex-col items-center py-2 px-1 text-primary-600 bg-primary-50 rounded-lg">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="cpu" className="lucide lucide-cpu w-5 h-5"><path d="M12 20v2"></path><path d="M12 2v2"></path><path d="M17 20v2"></path><path d="M17 2v2"></path><path d="M2 12h2"></path><path d="M2 17h2"></path><path d="M2 7h2"></path><path d="M20 12h2"></path><path d="M20 17h2"></path><path d="M20 7h2"></path><path d="M7 20v2"></path><path d="M7 2v2"></path><rect x="4" y="4" width="16" height="16" rx="2"></rect><rect x="8" y="8" width="8" height="8" rx="1"></rect></svg>
                <span className="text-xs mt-1 font-medium">Infrastructure</span>
            </button>
            <button className="flex flex-col items-center py-2 px-1 text-gray-400 hover:text-gray-600">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="settings" className="lucide lucide-settings w-5 h-5"><path d="M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915"></path><circle cx="12" cy="12" r="3"></circle></svg>
                <span className="text-xs mt-1">Config</span>
            </button>
        </div>
    </div>

    <script>
        // Initialize Lucide icons
        lucide.createIcons();
        
        document.addEventListener('DOMContentLoaded', function() {
            // Database action buttons
            const viewQueriesBtn = document.querySelector('button:contains("View Queries")');
            const backupBtn = document.querySelector('button:contains("Backup Now")');
            const optimizeBtn = document.querySelector('button:contains("Optimize")');

            // PostgreSQL actions
            document.querySelectorAll('button').forEach(btn => {
                const text = btn.textContent.trim();
                
                if (text === 'View Queries') {
                    btn.addEventListener('click', function() {
                        console.log('Opening PostgreSQL query analyzer...');
                        // Open query analyzer modal or page
                    });
                }
                
                if (text === 'Backup Now') {
                    btn.addEventListener('click', function() {
                        console.log('Starting PostgreSQL backup...');
                        this.textContent = 'Backing up...';
                        this.disabled = true;
                        
                        setTimeout(() => {
                            this.textContent = 'Backup Now';
                            this.disabled = false;
                            console.log('Backup completed successfully');
                        }, 3000);
                    });
                }
                
                if (text === 'Optimize') {
                    btn.addEventListener('click', function() {
                        const component = this.closest('.bg-white').querySelector('h3').textContent;
                        console.log(`Optimizing ${component}...`);
                        
                        this.textContent = 'Optimizing...';
                        this.disabled = true;
                        
                        setTimeout(() => {
                            this.textContent = 'Optimize';
                            this.disabled = false;
                            console.log(`${component} optimization completed`);
                        }, 5000);
                    });
                }
            });

            // Qdrant actions
            document.querySelectorAll('button').forEach(btn => {
                const text = btn.textContent.trim();
                
                if (text === 'View Collections') {
                    btn.addEventListener('click', function() {
                        console.log('Opening Qdrant collections viewer...');
                        // Open collections viewer
                    });
                }
                
                if (text === 'Reindex') {
                    btn.addEventListener('click', function() {
                        if (confirm('Reindexing will temporarily affect search performance. Continue?')) {
                            console.log('Starting Qdrant reindexing...');
                            this.textContent = 'Reindexing...';
                            this.disabled = true;
                            
                            setTimeout(() => {
                                this.textContent = 'Reindex';
                                this.disabled = false;
                                console.log('Reindexing completed');
                            }, 8000);
                        }
                    });
                }
            });

            // RabbitMQ actions
            document.querySelectorAll('button').forEach(btn => {
                const text = btn.textContent.trim();
                
                if (text === 'View Queues') {
                    btn.addEventListener('click', function() {
                        console.log('Opening RabbitMQ management interface...');
                        // Open RabbitMQ management
                    });
                }
                
                if (text === 'Purge Queue') {
                    btn.addEventListener('click', function() {
                        if (confirm('This will delete all messages in the selected queue. Continue?')) {
                            console.log('Purging RabbitMQ queue...');
                            // Implement queue purging
                        }
                    });
                }
            });

            // Redis actions
            document.querySelectorAll('button').forEach(btn => {
                const text = btn.textContent.trim();
                
                if (text === 'View Keys') {
                    btn.addEventListener('click', function() {
                        console.log('Opening Redis key browser...');
                        // Open Redis key browser
                    });
                }
                
                if (text === 'Flush Cache') {
                    btn.addEventListener('click', function() {
                        if (confirm('This will clear all cached data. Continue?')) {
                            console.log('Flushing Redis cache...');
                            this.textContent = 'Flushing...';
                            this.disabled = true;
                            
                            setTimeout(() => {
                                this.textContent = 'Flush Cache';
                                this.disabled = false;
                                
                                // Update cache stats
                                const keysCount = this.closest('.bg-white').querySelector('.text-lg.font-semibold');
                                if (keysCount && keysCount.textContent.includes('K')) {
                                    keysCount.textContent = '0';
                                }
                                
                                console.log('Cache flushed successfully');
                            }, 2000);
                        }
                    });
                }
            });

            // Monitoring system actions
            document.querySelectorAll('button').forEach(btn => {
                const text = btn.textContent.trim();
                
                if (text === 'View Events') {
                    btn.addEventListener('click', function() {
                        console.log('Opening EventBus event stream...');
                        // Open event stream viewer
                    });
                }
                
                if (text === 'View Metrics') {
                    btn.addEventListener('click', function() {
                        console.log('Opening Prometheus metrics...');
                        // Open Prometheus interface
                    });
                }
                
                if (text === 'Open Grafana') {
                    btn.addEventListener('click', function() {
                        console.log('Opening Grafana dashboards...');
                        // Open Grafana in new tab
                        window.open('/grafana', '_blank');
                    });
                }
            });

            // Global action buttons
            const refreshAllBtn = document.querySelector('button:has(i[data-lucide="refresh-cw"])');
            const exportBtn = document.querySelector('button:has(i[data-lucide="download"])');

            if (refreshAllBtn) {
                refreshAllBtn.addEventListener('click', function() {
                    console.log('Refreshing all infrastructure components...');
                    const icon = this.querySelector('i');
                    icon.classList.add('animate-spin');
                    
                    setTimeout(() => {
                        icon.classList.remove('animate-spin');
                        console.log('All components refreshed');
                    }, 3000);
                });
            }

            if (exportBtn) {
                exportBtn.addEventListener('click', function() {
                    console.log('Generating infrastructure report...');
                    this.textContent = 'Generating...';
                    this.disabled = true;
                    
                    setTimeout(() => {
                        this.innerHTML = '<i data-lucide="download" className="w-4 h-4 mr-2"></i>Export Report';
                        this.disabled = false;
                        lucide.createIcons();
                        
                        // Simulate file download
                        const link = document.createElement('a');
                        link.href = 'data:text/plain;charset=utf-8,Infrastructure Report - ' + new Date().toISOString();
                        link.download = 'infrastructure-report-' + new Date().toISOString().split('T')[0] + '.txt';
                        link.click();
                        
                        console.log('Infrastructure report downloaded');
                    }, 2000);
                });
            }

            // Real-time metrics updates
            function updateMetrics() {
                // Simulate real-time metric updates
                const metrics = {
                    'postgresql_connections': () => Math.floor(Math.random() * 20) + 40,
                    'postgresql_queries': () => Math.floor(Math.random() * 100) + 200,
                    'qdrant_vectors': () => '2.4M',
                    'redis_memory': () => Math.floor(Math.random() * 50) + 220 + 'MB',
                    'redis_hit_rate': () => (Math.random() * 5 + 92).toFixed(1) + '%',
                    'rabbitmq_messages': () => Math.floor(Math.random() * 100) + 100,
                    'eventbus_events': () => (Math.random() * 10 + 40).toFixed(1) + 'K'
                };

                // Update random metrics
                Object.keys(metrics).forEach(key => {
                    if (Math.random() < 0.3) { // 30% chance to update each metric
                        const value = metrics[key]();
                        console.log(`Updated ${key}:`, value);
                        // In real implementation, update the DOM elements
                    }
                });
            }

            // Update metrics every 30 seconds
            setInterval(updateMetrics, 30000);

            // Health check simulation
            function performHealthCheck() {
                console.log('Performing infrastructure health check...');
                
                // Simulate occasional issues (very rare)
                if (Math.random() < 0.05) { // 5% chance
                    console.log('Health check detected minor issue - investigating...');
                    // In real implementation, this would trigger alerts
                }
            }

            // Health check every 2 minutes
            setInterval(performHealthCheck, 120000);

            // Connection status monitoring
            function monitorConnections() {
                // Simulate connection monitoring
                const components = ['PostgreSQL', 'Qdrant', 'RabbitMQ', 'Redis', 'EventBus', 'Prometheus', 'Grafana'];
                
                components.forEach(component => {
                    // Simulate connection test
                    if (Math.random() < 0.02) { // 2% chance of connection issue
                        console.log(`Connection test failed for ${component} - retrying...`);
                        // In real implementation, this would trigger reconnection logic
                    }
                });
            }

            // Monitor connections every minute
            setInterval(monitorConnections, 60000);
        });
    </script>


    </div>
  );
};

export default Untitled1;