import React from 'react';

const Untitled1 = () => {
  return (
    <div>
      
    
    <nav className="bg-white border-b border-gray-200 px-4 py-3 sm:px-6">
        <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="file-text" className="lucide lucide-file-text w-6 h-6 text-white"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"></path><path d="M14 2v4a2 2 0 0 0 2 2h4"></path><path d="M10 9H8"></path><path d="M16 13H8"></path><path d="M16 17H8"></path></svg>
                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-gray-900">AI-Platform-ISO Admin</h1>
                        <p className="text-xs text-gray-500">Logs &amp; Audit Trail</p>
                    </div>
                </div>
            </div>
            <div className="flex items-center space-x-3">
                <div className="flex items-center space-x-2 px-3 py-1 bg-success-100 text-success-800 rounded-full text-sm font-medium">
                    <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></div>
                    <span>Live Monitoring</span>
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
                    <nav className="mt-5 flex-1 px-2 space-y-1"><div className="flex items-start space-x-3 hover:bg-gray-800 px-2 py-1 rounded">
                    <span className="text-gray-400 text-xs mt-1 w-20 flex-shrink-0">23:58:31</span>
                    <span className="bg-red-600 text-white px-2 py-0.5 rounded text-xs font-medium w-12 text-center flex-shrink-0">ERROR</span>
                    <span className="text-red-400 w-24 flex-shrink-0 text-xs">auth-service</span>
                    <span className="text-gray-300 flex-1">Notification sent</span>
                </div><div className="flex items-start space-x-3 hover:bg-gray-800 px-2 py-1 rounded">
                    <span className="text-gray-400 text-xs mt-1 w-20 flex-shrink-0">23:58:29</span>
                    <span className="bg-yellow-600 text-white px-2 py-0.5 rounded text-xs font-medium w-12 text-center flex-shrink-0">WARN</span>
                    <span className="text-yellow-400 w-24 flex-shrink-0 text-xs">auth-service</span>
                    <span className="text-gray-300 flex-1">User authentication successful</span>
                </div>
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
                        <a href="#" className="bg-primary-50 text-primary-700 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="file-text" className="lucide lucide-file-text text-primary-500 mr-3 h-5 w-5"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"></path><path d="M14 2v4a2 2 0 0 0 2 2h4"></path><path d="M10 9H8"></path><path d="M16 13H8"></path><path d="M16 17H8"></path></svg>
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
                                <h1 className="text-2xl font-bold text-gray-900">Logs &amp; Audit Trail</h1>
                                <p className="mt-1 text-sm text-gray-500">Monitor system logs, user activities, and security events</p>
                            </div>
                            <div className="mt-4 sm:mt-0 flex space-x-3">
                                <button className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="download" className="lucide lucide-download w-4 h-4 mr-2"><path d="M12 15V3"></path><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><path d="m7 10 5 5 5-5"></path></svg>
                                    Export Logs
                                </button>
                                <button className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="settings" className="lucide lucide-settings w-4 h-4 mr-2"><path d="M9.671 4.136a2.34 2.34 0 0 1 4.659 0 2.34 2.34 0 0 0 3.319 1.915 2.34 2.34 0 0 1 2.33 4.033 2.34 2.34 0 0 0 0 3.831 2.34 2.34 0 0 1-2.33 4.033 2.34 2.34 0 0 0-3.319 1.915 2.34 2.34 0 0 1-4.659 0 2.34 2.34 0 0 0-3.32-1.915 2.34 2.34 0 0 1-2.33-4.033 2.34 2.34 0 0 0 0-3.831A2.34 2.34 0 0 1 6.35 6.051a2.34 2.34 0 0 0 3.319-1.915"></path><circle cx="12" cy="12" r="3"></circle></svg>
                                    Configure
                                </button>
                            </div>
                        </div>
                    </div>

                    
                    <div className="mb-6">
                        <div className="border-b border-gray-200">
                            <nav className="-mb-px flex space-x-8">
                                <button className="border-primary-500 text-primary-600 whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="activity" className="lucide lucide-activity w-4 h-4 mr-2"><path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2"></path></svg>
                                    System Logs
                                    <span className="ml-2 bg-primary-100 text-primary-600 py-0.5 px-2 rounded-full text-xs font-medium">Live</span>
                                </button>
                                <button className="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="shield" className="lucide lucide-shield w-4 h-4 mr-2"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"></path></svg>
                                    Audit Trail
                                    <span className="ml-2 bg-gray-100 text-gray-600 py-0.5 px-2 rounded-full text-xs font-medium">1,247</span>
                                </button>
                                <button className="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="alert-triangle" className="lucide lucide-alert-triangle w-4 h-4 mr-2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>
                                    Error Logs
                                    <span className="ml-2 bg-danger-100 text-danger-600 py-0.5 px-2 rounded-full text-xs font-medium">23</span>
                                </button>
                                <button className="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="globe" className="lucide lucide-globe w-4 h-4 mr-2"><circle cx="12" cy="12" r="10"></circle><path d="M12 2a14.5 14.5 0 0 0 0 20 14.5 14.5 0 0 0 0-20"></path><path d="M2 12h20"></path></svg>
                                    API Logs
                                    <span className="ml-2 bg-gray-100 text-gray-600 py-0.5 px-2 rounded-full text-xs font-medium">5.2K</span>
                                </button>
                            </nav>
                        </div>
                    </div>

                    
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
                        <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0 lg:space-x-4">
                            <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-4">
                                <div className="relative">
                                    <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="search" className="lucide lucide-search h-4 w-4 text-gray-400"><path d="m21 21-4.34-4.34"></path><circle cx="11" cy="11" r="8"></circle></svg>
                                    </div>
                                    <input type="text" placeholder="Search logs..." className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 w-full sm:w-80" />
                                </div>
                                
                                <select className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                                    <option>All Levels</option>
                                    <option>DEBUG</option>
                                    <option>INFO</option>
                                    <option>WARN</option>
                                    <option>ERROR</option>
                                    <option>FATAL</option>
                                </select>
                                
                                <select className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                                    <option>All Services</option>
                                    <option>API Gateway</option>
                                    <option>Auth Service</option>
                                    <option>BIA Service</option>
                                    <option>Risk Service</option>
                                    <option>AI Orchestrator</option>
                                </select>
                                
                                <input type="datetime-local" className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500" />
                            </div>
                            
                            <div className="flex items-center space-x-2">
                                <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors" title="Auto-refresh">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="refresh-cw" className="lucide lucide-refresh-cw w-4 h-4"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"></path><path d="M21 3v5h-5"></path><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"></path><path d="M8 16H3v5"></path></svg>
                                </button>
                                <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors" title="Pause live updates">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="pause" className="lucide lucide-pause w-4 h-4"><rect x="14" y="3" width="5" height="18" rx="1"></rect><rect x="5" y="3" width="5" height="18" rx="1"></rect></svg>
                                </button>
                                <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors" title="Clear filters">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="x" className="lucide lucide-x w-4 h-4"><path d="M18 6 6 18"></path><path d="m6 6 12 12"></path></svg>
                                </button>
                            </div>
                        </div>
                    </div>

                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="activity" className="lucide lucide-activity w-4 h-4 text-blue-600"><path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2"></path></svg>
                                    </div>
                                </div>
                                <div className="ml-4">
                                    <p className="text-sm font-medium text-gray-500">Events/Min</p>
                                    <p className="text-2xl font-bold text-gray-900">1,247</p>
                                </div>
                            </div>
                            <div className="mt-4">
                                <div className="flex items-center text-sm">
                                    <span className="text-success-600 font-medium">+12%</span>
                                    <span className="text-gray-500 ml-1">vs last hour</span>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <div className="w-8 h-8 bg-danger-100 rounded-lg flex items-center justify-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="alert-triangle" className="lucide lucide-alert-triangle w-4 h-4 text-danger-600"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>
                                    </div>
                                </div>
                                <div className="ml-4">
                                    <p className="text-sm font-medium text-gray-500">Errors (24h)</p>
                                    <p className="text-2xl font-bold text-gray-900">23</p>
                                </div>
                            </div>
                            <div className="mt-4">
                                <div className="flex items-center text-sm">
                                    <span className="text-danger-600 font-medium">-8%</span>
                                    <span className="text-gray-500 ml-1">vs yesterday</span>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <div className="w-8 h-8 bg-warning-100 rounded-lg flex items-center justify-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="shield" className="lucide lucide-shield w-4 h-4 text-warning-600"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"></path></svg>
                                    </div>
                                </div>
                                <div className="ml-4">
                                    <p className="text-sm font-medium text-gray-500">Security Events</p>
                                    <p className="text-2xl font-bold text-gray-900">7</p>
                                </div>
                            </div>
                            <div className="mt-4">
                                <div className="flex items-center text-sm">
                                    <span className="text-warning-600 font-medium">2</span>
                                    <span className="text-gray-500 ml-1">require attention</span>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <div className="w-8 h-8 bg-success-100 rounded-lg flex items-center justify-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="database" className="lucide lucide-database w-4 h-4 text-success-600"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M3 5V19A9 3 0 0 0 21 19V5"></path><path d="M3 12A9 3 0 0 0 21 12"></path></svg>
                                    </div>
                                </div>
                                <div className="ml-4">
                                    <p className="text-sm font-medium text-gray-500">Storage Used</p>
                                    <p className="text-2xl font-bold text-gray-900">2.4GB</p>
                                </div>
                            </div>
                            <div className="mt-4">
                                <div className="flex items-center text-sm">
                                    <span className="text-gray-600 font-medium">78%</span>
                                    <span className="text-gray-500 ml-1">of 90-day retention</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
                        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                            <div>
                                <h3 className="text-lg font-semibold text-gray-900">Live System Logs</h3>
                                <p className="text-sm text-gray-500">Real-time log stream with automatic updates</p>
                            </div>
                            <div className="flex items-center space-x-2">
                                <div className="flex items-center space-x-2 text-sm text-gray-500">
                                    <div className="w-2 h-2 bg-success-500 rounded-full animate-pulse"></div>
                                    <span>Live</span>
                                </div>
                                <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="maximize-2" className="lucide lucide-maximize-2 w-4 h-4"><path d="M15 3h6v6"></path><path d="m21 3-7 7"></path><path d="m3 21 7-7"></path><path d="M9 21H3v-6"></path></svg>
                                </button>
                            </div>
                        </div>
                        
                        <div className="h-96 overflow-y-auto bg-gray-900 text-gray-100 font-mono text-sm">
                            <div className="p-4 space-y-1">
                                <div className="flex items-start space-x-3 hover:bg-gray-800 px-2 py-1 rounded">
                                    <span className="text-gray-400 text-xs mt-1 w-20 flex-shrink-0">14:23:45</span>
                                    <span className="bg-blue-600 text-white px-2 py-0.5 rounded text-xs font-medium w-12 text-center flex-shrink-0">INFO</span>
                                    <span className="text-blue-400 w-24 flex-shrink-0 text-xs">api-gateway</span>
                                    <span className="text-gray-300 flex-1">User authentication successful for user_id: 12847</span>
                                </div>
                                
                                <div className="flex items-start space-x-3 hover:bg-gray-800 px-2 py-1 rounded">
                                    <span className="text-gray-400 text-xs mt-1 w-20 flex-shrink-0">14:23:44</span>
                                    <span className="bg-green-600 text-white px-2 py-0.5 rounded text-xs font-medium w-12 text-center flex-shrink-0">DEBUG</span>
                                    <span className="text-green-400 w-24 flex-shrink-0 text-xs">bia-service</span>
                                    <span className="text-gray-300 flex-1">BIA workflow step completed: dependency_mapping</span>
                                </div>
                                
                                <div className="flex items-start space-x-3 hover:bg-gray-800 px-2 py-1 rounded">
                                    <span className="text-gray-400 text-xs mt-1 w-20 flex-shrink-0">14:23:43</span>
                                    <span className="bg-yellow-600 text-white px-2 py-0.5 rounded text-xs font-medium w-12 text-center flex-shrink-0">WARN</span>
                                    <span className="text-yellow-400 w-24 flex-shrink-0 text-xs">ai-orchestrator</span>
                                    <span className="text-gray-300 flex-1">High API usage detected: 95% of rate limit reached</span>
                                </div>
                                
                                <div className="flex items-start space-x-3 hover:bg-gray-800 px-2 py-1 rounded">
                                    <span className="text-gray-400 text-xs mt-1 w-20 flex-shrink-0">14:23:42</span>
                                    <span className="bg-blue-600 text-white px-2 py-0.5 rounded text-xs font-medium w-12 text-center flex-shrink-0">INFO</span>
                                    <span className="text-blue-400 w-24 flex-shrink-0 text-xs">risk-service</span>
                                    <span className="text-gray-300 flex-1">Risk assessment completed for organization: global-healthcare</span>
                                </div>
                                
                                <div className="flex items-start space-x-3 hover:bg-gray-800 px-2 py-1 rounded">
                                    <span className="text-gray-400 text-xs mt-1 w-20 flex-shrink-0">14:23:41</span>
                                    <span className="bg-red-600 text-white px-2 py-0.5 rounded text-xs font-medium w-12 text-center flex-shrink-0">ERROR</span>
                                    <span className="text-red-400 w-24 flex-shrink-0 text-xs">db-service</span>
                                    <span className="text-gray-300 flex-1">Connection timeout to PostgreSQL: connection_pool_exhausted</span>
                                </div>
                                
                                <div className="flex items-start space-x-3 hover:bg-gray-800 px-2 py-1 rounded">
                                    <span className="text-gray-400 text-xs mt-1 w-20 flex-shrink-0">14:23:40</span>
                                    <span className="bg-blue-600 text-white px-2 py-0.5 rounded text-xs font-medium w-12 text-center flex-shrink-0">INFO</span>
                                    <span className="text-blue-400 w-24 flex-shrink-0 text-xs">auth-service</span>
                                    <span className="text-gray-300 flex-1">JWT token refreshed for session: sess_9x8y7z6w5v</span>
                                </div>
                                
                                <div className="flex items-start space-x-3 hover:bg-gray-800 px-2 py-1 rounded">
                                    <span className="text-gray-400 text-xs mt-1 w-20 flex-shrink-0">14:23:39</span>
                                    <span className="bg-purple-600 text-white px-2 py-0.5 rounded text-xs font-medium w-12 text-center flex-shrink-0">AUDIT</span>
                                    <span className="text-purple-400 w-24 flex-shrink-0 text-xs">audit-service</span>
                                    <span className="text-gray-300 flex-1">User action logged: document_download by admin@company.com</span>
                                </div>
                                
                                <div className="flex items-start space-x-3 hover:bg-gray-800 px-2 py-1 rounded">
                                    <span className="text-gray-400 text-xs mt-1 w-20 flex-shrink-0">14:23:38</span>
                                    <span className="bg-green-600 text-white px-2 py-0.5 rounded text-xs font-medium w-12 text-center flex-shrink-0">DEBUG</span>
                                    <span className="text-green-400 w-24 flex-shrink-0 text-xs">ai-specialist</span>
                                    <span className="text-gray-300 flex-1">LLM request processed: tokens_used=1247, response_time=850ms</span>
                                </div>
                                
                                <div className="flex items-start space-x-3 hover:bg-gray-800 px-2 py-1 rounded">
                                    <span className="text-gray-400 text-xs mt-1 w-20 flex-shrink-0">14:23:37</span>
                                    <span className="bg-blue-600 text-white px-2 py-0.5 rounded text-xs font-medium w-12 text-center flex-shrink-0">INFO</span>
                                    <span className="text-blue-400 w-24 flex-shrink-0 text-xs">notification</span>
                                    <span className="text-gray-300 flex-1">Email notification sent: compliance_reminder to 45 users</span>
                                </div>
                                
                                <div className="flex items-start space-x-3 hover:bg-gray-800 px-2 py-1 rounded">
                                    <span className="text-gray-400 text-xs mt-1 w-20 flex-shrink-0">14:23:36</span>
                                    <span className="bg-yellow-600 text-white px-2 py-0.5 rounded text-xs font-medium w-12 text-center flex-shrink-0">WARN</span>
                                    <span className="text-yellow-400 w-24 flex-shrink-0 text-xs">file-service</span>
                                    <span className="text-gray-300 flex-1">Large file upload detected: 45MB document.pdf</span>
                                </div>
                                
                                <div className="flex items-start space-x-3 hover:bg-gray-800 px-2 py-1 rounded">
                                    <span className="text-gray-400 text-xs mt-1 w-20 flex-shrink-0">14:23:35</span>
                                    <span className="bg-blue-600 text-white px-2 py-0.5 rounded text-xs font-medium w-12 text-center flex-shrink-0">INFO</span>
                                    <span className="text-blue-400 w-24 flex-shrink-0 text-xs">exercise</span>
                                    <span className="text-gray-300 flex-1">Exercise simulation started: digital_twin_scenario_001</span>
                                </div>
                                
                                <div className="flex items-start space-x-3 hover:bg-gray-800 px-2 py-1 rounded">
                                    <span className="text-gray-400 text-xs mt-1 w-20 flex-shrink-0">14:23:34</span>
                                    <span className="bg-green-600 text-white px-2 py-0.5 rounded text-xs font-medium w-12 text-center flex-shrink-0">DEBUG</span>
                                    <span className="text-green-400 w-24 flex-shrink-0 text-xs">vector-db</span>
                                    <span className="text-gray-300 flex-1">Vector search completed: 1247 documents indexed, query_time=23ms</span>
                                </div>
                                
                                <div className="flex items-start space-x-3 hover:bg-gray-800 px-2 py-1 rounded">
                                    <span className="text-gray-400 text-xs mt-1 w-20 flex-shrink-0">14:23:33</span>
                                    <span className="bg-purple-600 text-white px-2 py-0.5 rounded text-xs font-medium w-12 text-center flex-shrink-0">AUDIT</span>
                                    <span className="text-purple-400 w-24 flex-shrink-0 text-xs">audit-service</span>
                                    <span className="text-gray-300 flex-1">Configuration change: backup_retention updated from 30 to 90 days</span>
                                </div>
                                
                                <div className="flex items-start space-x-3 hover:bg-gray-800 px-2 py-1 rounded">
                                    <span className="text-gray-400 text-xs mt-1 w-20 flex-shrink-0">14:23:32</span>
                                    <span className="bg-blue-600 text-white px-2 py-0.5 rounded text-xs font-medium w-12 text-center flex-shrink-0">INFO</span>
                                    <span className="text-blue-400 w-24 flex-shrink-0 text-xs">compliance</span>
                                    <span className="text-gray-300 flex-1">ISO 22301 compliance score updated: 87% (+2% improvement)</span>
                                </div>
                            </div>
                        </div>
                        
                        <div className="px-6 py-3 border-t border-gray-200 bg-gray-50">
                            <div className="flex items-center justify-between text-sm text-gray-500">
                                <div className="flex items-center space-x-4">
                                    <span>Showing last 100 entries</span>
                                    <span>•</span>
                                    <span>Auto-refresh: ON</span>
                                    <span>•</span>
                                    <span>Retention: 90 days</span>
                                </div>
                                <div className="flex items-center space-x-2">
                                    <button className="text-primary-600 hover:text-primary-700 font-medium">View All</button>
                                    <span>•</span>
                                    <button className="text-primary-600 hover:text-primary-700 font-medium">Download</button>
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
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="file-text" className="lucide lucide-file-text w-5 h-5"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"></path><path d="M14 2v4a2 2 0 0 0 2 2h4"></path><path d="M10 9H8"></path><path d="M16 13H8"></path><path d="M16 17H8"></path></svg>
                <span className="text-xs mt-1 font-medium">Logs</span>
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
            let isLiveMode = true;
            let autoRefreshInterval;
            
            // Tab switching
            const tabs = document.querySelectorAll('nav button');
            tabs.forEach(tab => {
                tab.addEventListener('click', function() {
                    // Remove active state from all tabs
                    tabs.forEach(t => {
                        t.className = 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center';
                    });
                    
                    // Add active state to clicked tab
                    this.className = 'border-primary-500 text-primary-600 whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm flex items-center';
                    
                    const tabName = this.textContent.trim().split('\n')[0];
                    console.log(`Switched to tab: ${tabName}`);
                    
                    // In real implementation, load different log types
                    loadLogType(tabName.toLowerCase().replace(' ', '_'));
                });
            });
            
            function loadLogType(type) {
                console.log(`Loading ${type} logs`);
                // In real implementation, fetch logs from API based on type
            }
            
            // Search functionality
            const searchInput = document.querySelector('input[placeholder="Search logs..."]');
            if (searchInput) {
                searchInput.addEventListener('input', function() {
                    const query = this.value.toLowerCase();
                    console.log(`Searching logs for: ${query}`);
                    // In real implementation, filter logs or make API call
                });
            }
            
            // Filter dropdowns
            const filterSelects = document.querySelectorAll('select');
            filterSelects.forEach(select => {
                select.addEventListener('change', function() {
                    console.log(`Filter changed: ${this.value}`);
                    // In real implementation, apply filters
                });
            });
            
            // Date/time filter
            const dateInput = document.querySelector('input[type="datetime-local"]');
            if (dateInput) {
                dateInput.addEventListener('change', function() {
                    console.log(`Date filter changed: ${this.value}`);
                    // In real implementation, filter logs by date
                });
            }
            
            // Control buttons
            const refreshButton = document.querySelector('button[title="Auto-refresh"]');
            const pauseButton = document.querySelector('button[title="Pause live updates"]');
            const clearButton = document.querySelector('button[title="Clear filters"]');
            
            if (refreshButton) {
                refreshButton.addEventListener('click', function() {
                    console.log('Manual refresh triggered');
                    const icon = this.querySelector('i');
                    icon.style.animation = 'spin 1s linear';
                    
                    setTimeout(() => {
                        icon.style.animation = '';
                    }, 1000);
                    
                    // In real implementation, fetch fresh logs
                    refreshLogs();
                });
            }
            
            if (pauseButton) {
                pauseButton.addEventListener('click', function() {
                    isLiveMode = !isLiveMode;
                    const icon = this.querySelector('i');
                    
                    if (isLiveMode) {
                        icon.setAttribute('data-lucide', 'pause');
                        startAutoRefresh();
                        console.log('Live mode enabled');
                    } else {
                        icon.setAttribute('data-lucide', 'play');
                        stopAutoRefresh();
                        console.log('Live mode paused');
                    }
                    
                    lucide.createIcons();
                });
            }
            
            if (clearButton) {
                clearButton.addEventListener('click', function() {
                    console.log('Clearing all filters');
                    
                    // Clear search
                    if (searchInput) searchInput.value = '';
                    
                    // Reset dropdowns
                    filterSelects.forEach(select => {
                        select.selectedIndex = 0;
                    });
                    
                    // Clear date filter
                    if (dateInput) dateInput.value = '';
                    
                    // In real implementation, reload logs without filters
                    refreshLogs();
                });
            }
            
            // Export logs
            const exportButton = document.querySelector('button:has(i[data-lucide="download"])');
            if (exportButton) {
                exportButton.addEventListener('click', function() {
                    console.log('Exporting logs');
                    // In real implementation, generate and download log file
                });
            }
            
            // Configure button
            const configButton = document.querySelector('button:has(i[data-lucide="settings"])');
            if (configButton) {
                configButton.addEventListener('click', function() {
                    console.log('Opening log configuration');
                    // In real implementation, open configuration modal
                });
            }
            
            // Log stream interactions
            const logEntries = document.querySelectorAll('.hover\\:bg-gray-800');
            logEntries.forEach(entry => {
                entry.addEventListener('click', function() {
                    const timestamp = this.querySelector('.w-20').textContent;
                    const level = this.querySelector('.w-12').textContent;
                    const service = this.querySelector('.w-24').textContent;
                    const message = this.querySelector('.flex-1').textContent;
                    
                    console.log('Log entry clicked:', {
                        timestamp,
                        level,
                        service,
                        message
                    });
                    
                    // In real implementation, show detailed log entry modal
                });
            });
            
            // Auto-refresh functionality
            function startAutoRefresh() {
                if (autoRefreshInterval) clearInterval(autoRefreshInterval);
                
                autoRefreshInterval = setInterval(() => {
                    if (isLiveMode) {
                        addNewLogEntry();
                    }
                }, 2000); // Add new log every 2 seconds
            }
            
            function stopAutoRefresh() {
                if (autoRefreshInterval) {
                    clearInterval(autoRefreshInterval);
                    autoRefreshInterval = null;
                }
            }
            
            function refreshLogs() {
                console.log('Refreshing logs from API');
                // In real implementation, fetch fresh logs from API
            }
            
            function addNewLogEntry() {
                const logContainer = document.querySelector('.space-y-1');
                if (!logContainer) return;
                
                const levels = ['INFO', 'DEBUG', 'WARN', 'ERROR'];
                const services = ['api-gateway', 'auth-service', 'bia-service', 'risk-service', 'ai-orchestrator'];
                const messages = [
                    'User authentication successful',
                    'Workflow step completed',
                    'API request processed',
                    'Database query executed',
                    'Cache updated successfully',
                    'File upload completed',
                    'Notification sent'
                ];
                
                const level = levels[Math.floor(Math.random() * levels.length)];
                const service = services[Math.floor(Math.random() * services.length)];
                const message = messages[Math.floor(Math.random() * messages.length)];
                const timestamp = new Date().toLocaleTimeString('en-US', { hour12: false });
                
                const levelColors = {
                    'INFO': 'bg-blue-600',
                    'DEBUG': 'bg-green-600',
                    'WARN': 'bg-yellow-600',
                    'ERROR': 'bg-red-600'
                };
                
                const serviceColors = {
                    'INFO': 'text-blue-400',
                    'DEBUG': 'text-green-400',
                    'WARN': 'text-yellow-400',
                    'ERROR': 'text-red-400'
                };
                
                const newEntry = document.createElement('div');
                newEntry.className = 'flex items-start space-x-3 hover:bg-gray-800 px-2 py-1 rounded';
                newEntry.innerHTML = `
                    <span className="text-gray-400 text-xs mt-1 w-20 flex-shrink-0">${timestamp}</span>
                    <span className="${levelColors[level]} text-white px-2 py-0.5 rounded text-xs font-medium w-12 text-center flex-shrink-0">${level}</span>
                    <span className="${serviceColors[level]} w-24 flex-shrink-0 text-xs">${service}</span>
                    <span className="text-gray-300 flex-1">${message}</span>
                `;
                
                // Add to top of log container
                logContainer.insertBefore(newEntry, logContainer.firstChild);
                
                // Remove oldest entry if more than 20 entries
                const entries = logContainer.children;
                if (entries.length > 20) {
                    logContainer.removeChild(entries[entries.length - 1]);
                }
                
                // Add click handler to new entry
                newEntry.addEventListener('click', function() {
                    console.log('New log entry clicked:', {
                        timestamp,
                        level,
                        service,
                        message
                    });
                });
            }
            
            // Start auto-refresh
            startAutoRefresh();
            
            // Keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                // Ctrl/Cmd + K to focus search
                if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                    e.preventDefault();
                    searchInput?.focus();
                }
                
                // Space to pause/resume live mode
                if (e.key === ' ' && !searchInput?.matches(':focus')) {
                    e.preventDefault();
                    pauseButton?.click();
                }
                
                // R to refresh
                if (e.key === 'r' && !searchInput?.matches(':focus')) {
                    e.preventDefault();
                    refreshButton?.click();
                }
                
                // C to clear filters
                if (e.key === 'c' && !searchInput?.matches(':focus')) {
                    e.preventDefault();
                    clearButton?.click();
                }
                
                // Escape to clear search
                if (e.key === 'Escape' && searchInput === document.activeElement) {
                    searchInput.value = '';
                    searchInput.blur();
                }
            });
            
            // Update stats periodically
            function updateStats() {
                const statsElements = document.querySelectorAll('.text-2xl.font-bold.text-gray-900');
                
                statsElements.forEach((element, index) => {
                    const currentValue = parseInt(element.textContent.replace(/[^0-9]/g, ''));
                    let newValue;
                    
                    switch(index) {
                        case 0: // Events/Min
                            newValue = Math.max(1000, currentValue + Math.floor(Math.random() * 100) - 50);
                            break;
                        case 1: // Errors
                            newValue = Math.max(0, currentValue + Math.floor(Math.random() * 3) - 1);
                            break;
                        case 2: // Security Events
                            newValue = Math.max(0, currentValue + Math.floor(Math.random() * 2) - 1);
                            break;
                        case 3: // Storage
                            newValue = currentValue; // Keep storage stable
                            break;
                    }
                    
                    if (newValue !== undefined && newValue !== currentValue) {
                        element.textContent = index === 3 ? `${(newValue / 1000).toFixed(1)}GB` : newValue.toLocaleString();
                    }
                });
            }
            
            // Update stats every 30 seconds
            setInterval(updateStats, 30000);
            
            // Cleanup on page unload
            window.addEventListener('beforeunload', function() {
                stopAutoRefresh();
            });
        });
        
        // Add CSS for animations
        const style = document.createElement('style');
        style.textContent = `
            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }
            
            .animate-pulse {
                animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
            }
            
            @keyframes pulse {
                0%, 100% {
                    opacity: 1;
                }
                50% {
                    opacity: .5;
                }
            }
        `;
        document.head.appendChild(style);
    </script>


    </div>
  );
};

export default Untitled1;