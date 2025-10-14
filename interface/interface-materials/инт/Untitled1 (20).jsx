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
                        <p className="text-xs text-gray-500">System Administration Panel</p>
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
                    <span className="absolute -top-1 -right-1 w-3 h-3 bg-danger-500 rounded-full flex items-center justify-center">
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
                        <a href="#" className="bg-danger-50 text-danger-700 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="layout-dashboard" className="lucide lucide-layout-dashboard text-danger-500 mr-3 h-5 w-5"><rect width="7" height="9" x="3" y="3" rx="1"></rect><rect width="7" height="5" x="14" y="3" rx="1"></rect><rect width="7" height="9" x="14" y="12" rx="1"></rect><rect width="7" height="5" x="3" y="16" rx="1"></rect></svg>
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
                                <h1 className="text-2xl font-bold text-gray-900">System Administration</h1>
                                <p className="mt-1 text-sm text-gray-500">Monitor and manage the AI-Platform-ISO infrastructure</p>
                            </div>
                            <div className="mt-4 sm:mt-0 flex space-x-3">
                                <button className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="download" className="lucide lucide-download w-4 h-4 mr-2"><path d="M12 15V3"></path><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><path d="m7 10 5 5 5-5"></path></svg>
                                    Export Report
                                </button>
                                <button className="bg-danger-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-danger-700 transition-colors flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="alert-triangle" className="lucide lucide-alert-triangle w-4 h-4 mr-2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>
                                    Emergency Mode
                                </button>
                            </div>
                        </div>
                    </div>

                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                        
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Platform Health</p>
                                    <p className="text-2xl font-bold text-success-600">99.9%</p>
                                    <p className="text-xs text-gray-500 mt-1">Uptime: 45d 12h 30m</p>
                                </div>
                                <div className="w-12 h-12 bg-success-100 rounded-full flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check-circle" className="lucide lucide-check-circle w-6 h-6 text-success-600"><path d="M21.801 10A10 10 0 1 1 17 3.335"></path><path d="m9 11 3 3L22 4"></path></svg>
                                </div>
                            </div>
                        </div>

                        
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Organizations</p>
                                    <p className="text-2xl font-bold text-gray-900">247</p>
                                    <p className="text-xs text-success-600 mt-1">+12 this month</p>
                                </div>
                                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="building" className="lucide lucide-building w-6 h-6 text-blue-600"><path d="M12 10h.01"></path><path d="M12 14h.01"></path><path d="M12 6h.01"></path><path d="M16 10h.01"></path><path d="M16 14h.01"></path><path d="M16 6h.01"></path><path d="M8 10h.01"></path><path d="M8 14h.01"></path><path d="M8 6h.01"></path><path d="M9 22v-3a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v3"></path><rect x="4" y="2" width="16" height="20" rx="2"></rect></svg>
                                </div>
                            </div>
                        </div>

                        
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Active Users</p>
                                    <p className="text-2xl font-bold text-gray-900">1,847</p>
                                    <p className="text-xs text-success-600 mt-1">+5.2% from yesterday</p>
                                </div>
                                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="users" className="lucide lucide-users w-6 h-6 text-green-600"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path><path d="M16 3.128a4 4 0 0 1 0 7.744"></path><path d="M22 21v-2a4 4 0 0 0-3-3.87"></path><circle cx="9" cy="7" r="4"></circle></svg>
                                </div>
                            </div>
                        </div>

                        
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">API Calls Today</p>
                                    <p className="text-2xl font-bold text-gray-900">2.4M</p>
                                    <p className="text-xs text-warning-600 mt-1">Peak: 145k/hour</p>
                                </div>
                                <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="zap" className="lucide lucide-zap w-6 h-6 text-purple-600"><path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"></path></svg>
                                </div>
                            </div>
                        </div>
                    </div>

                    
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                        
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-lg font-semibold text-gray-900">Platform Services (12)</h3>
                                <div className="flex items-center space-x-2">
                                    <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-success-100 text-success-800">
                                        <span className="w-2 h-2 bg-success-500 rounded-full mr-1"></span>
                                        All Healthy
                                    </span>
                                </div>
                            </div>
                            <div className="space-y-3">
                                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <div>
                                            <span className="text-sm font-medium text-gray-900">API Gateway</span>
                                            <p className="text-xs text-gray-500">:8000</p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm text-gray-600">99.9%</p>
                                        <p className="text-xs text-gray-500">245ms avg</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <div>
                                            <span className="text-sm font-medium text-gray-900">Auth Service</span>
                                            <p className="text-xs text-gray-500">:8001</p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm text-gray-600">100%</p>
                                        <p className="text-xs text-gray-500">120ms avg</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <div>
                                            <span className="text-sm font-medium text-gray-900">User Service</span>
                                            <p className="text-xs text-gray-500">:8002</p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm text-gray-600">99.8%</p>
                                        <p className="text-xs text-gray-500">180ms avg</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-center justify-between p-3 bg-warning-50 rounded-lg hover:bg-warning-100 cursor-pointer transition-colors">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-warning-500 rounded-full"></div>
                                        <div>
                                            <span className="text-sm font-medium text-gray-900">Notification Service</span>
                                            <p className="text-xs text-gray-500">:8003</p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm text-warning-600">95.2%</p>
                                        <p className="text-xs text-gray-500">850ms avg</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <div>
                                            <span className="text-sm font-medium text-gray-900">File Service</span>
                                            <p className="text-xs text-gray-500">:8004</p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm text-gray-600">99.7%</p>
                                        <p className="text-xs text-gray-500">150ms avg</p>
                                    </div>
                                </div>
                                
                                <div className="text-center py-2">
                                    <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">View All Platform Services</button>
                                </div>
                            </div>
                        </div>

                        
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-lg font-semibold text-gray-900">Intelligent Core (11)</h3>
                                <div className="flex items-center space-x-2">
                                    <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-success-100 text-success-800">
                                        <span className="w-2 h-2 bg-success-500 rounded-full mr-1"></span>
                                        AI Active
                                    </span>
                                </div>
                            </div>
                            <div className="space-y-3">
                                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <div>
                                            <span className="text-sm font-medium text-gray-900">AI Orchestrator</span>
                                            <p className="text-xs text-gray-500">:9000</p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm text-gray-600">99.5%</p>
                                        <p className="text-xs text-gray-500">1.2s avg</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <div>
                                            <span className="text-sm font-medium text-gray-900">BIA Specialist</span>
                                            <p className="text-xs text-gray-500">:9001</p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm text-gray-600">100%</p>
                                        <p className="text-xs text-gray-500">800ms avg</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <div>
                                            <span className="text-sm font-medium text-gray-900">Risk Specialist</span>
                                            <p className="text-xs text-gray-500">:9002</p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm text-gray-600">99.9%</p>
                                        <p className="text-xs text-gray-500">650ms avg</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <div>
                                            <span className="text-sm font-medium text-gray-900">Plan Specialist</span>
                                            <p className="text-xs text-gray-500">:9003</p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm text-gray-600">98.7%</p>
                                        <p className="text-xs text-gray-500">920ms avg</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 cursor-pointer transition-colors">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <div>
                                            <span className="text-sm font-medium text-gray-900">RAG Engine</span>
                                            <p className="text-xs text-gray-500">:9010</p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm text-gray-600">99.8%</p>
                                        <p className="text-xs text-gray-500">450ms avg</p>
                                    </div>
                                </div>
                                
                                <div className="text-center py-2">
                                    <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">View All AI Services</button>
                                </div>
                            </div>
                        </div>
                    </div>

                    
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                        
                        <div className="lg:col-span-2 bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-lg font-semibold text-gray-900">System Metrics</h3>
                                <select className="text-sm border border-gray-300 rounded px-2 py-1">
                                    <option>Last 24 hours</option>
                                    <option>Last 7 days</option>
                                    <option>Last 30 days</option>
                                </select>
                            </div>
                            <div className="h-80 overflow-hidden">
                                <canvas id="systemMetricsChart" className="w-full h-full" width="1366" height="640" style={{display: 'block', boxSizing: 'border-box', height: '320px', width: '683px'}}></canvas>
                            </div>
                        </div>

                        
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-lg font-semibold text-gray-900">Critical Alerts</h3>
                                <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-danger-100 text-danger-800">
                                    2 Active
                                </span>
                            </div>
                            <div className="space-y-3 max-h-80 overflow-y-auto">
                                <div className="p-3 bg-danger-50 border border-danger-200 rounded-lg">
                                    <div className="flex items-start space-x-3">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="alert-triangle" className="lucide lucide-alert-triangle w-5 h-5 text-danger-500 mt-0.5"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>
                                        <div className="flex-1">
                                            <p className="text-sm font-medium text-danger-900">High Memory Usage</p>
                                            <p className="text-xs text-danger-700 mt-1">Notification Service using 95% memory</p>
                                            <p className="text-xs text-gray-500 mt-1">5 minutes ago</p>
                                        </div>
                                    </div>
                                </div>
                                
                                <div className="p-3 bg-warning-50 border border-warning-200 rounded-lg">
                                    <div className="flex items-start space-x-3">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="clock" className="lucide lucide-clock w-5 h-5 text-warning-500 mt-0.5"><path d="M12 6v6l4 2"></path><circle cx="12" cy="12" r="10"></circle></svg>
                                        <div className="flex-1">
                                            <p className="text-sm font-medium text-warning-900">Slow Response Time</p>
                                            <p className="text-xs text-warning-700 mt-1">AI Orchestrator response time &gt; 2s</p>
                                            <p className="text-xs text-gray-500 mt-1">12 minutes ago</p>
                                        </div>
                                    </div>
                                </div>
                                
                                <div className="p-3 bg-blue-50 border border-blue-200 rounded-lg">
                                    <div className="flex items-start space-x-3">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="info" className="lucide lucide-info w-5 h-5 text-blue-500 mt-0.5"><circle cx="12" cy="12" r="10"></circle><path d="M12 16v-4"></path><path d="M12 8h.01"></path></svg>
                                        <div className="flex-1">
                                            <p className="text-sm font-medium text-blue-900">Scheduled Maintenance</p>
                                            <p className="text-xs text-blue-700 mt-1">Database backup scheduled for 2:00 AM</p>
                                            <p className="text-xs text-gray-500 mt-1">1 hour ago</p>
                                        </div>
                                    </div>
                                </div>
                                
                                <div className="p-3 bg-success-50 border border-success-200 rounded-lg">
                                    <div className="flex items-start space-x-3">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check-circle" className="lucide lucide-check-circle w-5 h-5 text-success-500 mt-0.5"><path d="M21.801 10A10 10 0 1 1 17 3.335"></path><path d="m9 11 3 3L22 4"></path></svg>
                                        <div className="flex-1">
                                            <p className="text-sm font-medium text-success-900">Service Restored</p>
                                            <p className="text-xs text-success-700 mt-1">File Service back to normal operation</p>
                                            <p className="text-xs text-gray-500 mt-1">2 hours ago</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="mt-4 pt-3 border-t border-gray-200">
                                <button className="w-full text-sm text-primary-600 hover:text-primary-700 font-medium">View All Alerts</button>
                            </div>
                        </div>
                    </div>

                    
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-lg font-semibold text-gray-900">Infrastructure Status</h3>
                                <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">Manage</button>
                            </div>
                            <div className="space-y-4">
                                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-10 h-10 bg-success-100 rounded-lg flex items-center justify-center">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="database" className="lucide lucide-database w-5 h-5 text-success-600"><ellipse cx="12" cy="5" rx="9" ry="3"></ellipse><path d="M3 5V19A9 3 0 0 0 21 19V5"></path><path d="M3 12A9 3 0 0 0 21 12"></path></svg>
                                        </div>
                                        <div>
                                            <p className="text-sm font-medium text-gray-900">PostgreSQL</p>
                                            <p className="text-xs text-gray-500">Primary database cluster</p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-success-100 text-success-800">Healthy</span>
                                        <p className="text-xs text-gray-500 mt-1">45/100 connections</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-10 h-10 bg-success-100 rounded-lg flex items-center justify-center">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="zap" className="lucide lucide-zap w-5 h-5 text-success-600"><path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"></path></svg>
                                        </div>
                                        <div>
                                            <p className="text-sm font-medium text-gray-900">Redis</p>
                                            <p className="text-xs text-gray-500">Cache and session store</p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-success-100 text-success-800">Healthy</span>
                                        <p className="text-xs text-gray-500 mt-1">2.1GB / 8GB used</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-10 h-10 bg-success-100 rounded-lg flex items-center justify-center">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="shuffle" className="lucide lucide-shuffle w-5 h-5 text-success-600"><path d="m18 14 4 4-4 4"></path><path d="m18 2 4 4-4 4"></path><path d="M2 18h1.973a4 4 0 0 0 3.3-1.7l5.454-8.6a4 4 0 0 1 3.3-1.7H22"></path><path d="M2 6h1.972a4 4 0 0 1 3.6 2.2"></path><path d="M22 18h-6.041a4 4 0 0 1-3.3-1.8l-.359-.45"></path></svg>
                                        </div>
                                        <div>
                                            <p className="text-sm font-medium text-gray-900">RabbitMQ</p>
                                            <p className="text-xs text-gray-500">Message broker</p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-success-100 text-success-800">Healthy</span>
                                        <p className="text-xs text-gray-500 mt-1">12 queues active</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-10 h-10 bg-success-100 rounded-lg flex items-center justify-center">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="brain" className="lucide lucide-brain w-5 h-5 text-success-600"><path d="M12 18V5"></path><path d="M15 13a4.17 4.17 0 0 1-3-4 4.17 4.17 0 0 1-3 4"></path><path d="M17.598 6.5A3 3 0 1 0 12 5a3 3 0 1 0-5.598 1.5"></path><path d="M17.997 5.125a4 4 0 0 1 2.526 5.77"></path><path d="M18 18a4 4 0 0 0 2-7.464"></path><path d="M19.967 17.483A4 4 0 1 1 12 18a4 4 0 1 1-7.967-.517"></path><path d="M6 18a4 4 0 0 1-2-7.464"></path><path d="M6.003 5.125a4 4 0 0 0-2.526 5.77"></path></svg>
                                        </div>
                                        <div>
                                            <p className="text-sm font-medium text-gray-900">Qdrant</p>
                                            <p className="text-xs text-gray-500">Vector database</p>
                                        </div>
                                    </div>
                                    <div className="text-right">
                                        <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-success-100 text-success-800">Healthy</span>
                                        <p className="text-xs text-gray-500 mt-1">1.2M vectors indexed</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-lg font-semibold text-gray-900">Recent Admin Activity</h3>
                                <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">View Audit Log</button>
                            </div>
                            <div className="space-y-3 max-h-80 overflow-y-auto">
                                <div className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                                    <div className="w-8 h-8 bg-danger-100 rounded-full flex items-center justify-center">
                                        <span className="text-xs font-medium text-danger-600">SA</span>
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-sm font-medium text-gray-900">Service Restart</p>
                                        <p className="text-xs text-gray-600">Restarted Notification Service due to memory leak</p>
                                        <p className="text-xs text-gray-500 mt-1">5 minutes ago</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
                                        <span className="text-xs font-medium text-blue-600">JD</span>
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-sm font-medium text-gray-900">User Created</p>
                                        <p className="text-xs text-gray-600">Created admin user for TechCorp organization</p>
                                        <p className="text-xs text-gray-500 mt-1">15 minutes ago</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                                    <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
                                        <span className="text-xs font-medium text-green-600">MK</span>
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-sm font-medium text-gray-900">Configuration Update</p>
                                        <p className="text-xs text-gray-600">Updated AI model configuration for better performance</p>
                                        <p className="text-xs text-gray-500 mt-1">1 hour ago</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                                    <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
                                        <span className="text-xs font-medium text-purple-600">SA</span>
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-sm font-medium text-gray-900">Backup Completed</p>
                                        <p className="text-xs text-gray-600">Scheduled database backup completed successfully</p>
                                        <p className="text-xs text-gray-500 mt-1">2 hours ago</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                                    <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center">
                                        <span className="text-xs font-medium text-yellow-600">JD</span>
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-sm font-medium text-gray-900">Organization Suspended</p>
                                        <p className="text-xs text-gray-600">Suspended FailedCorp due to payment issues</p>
                                        <p className="text-xs text-gray-500 mt-1">3 hours ago</p>
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
            <button className="flex flex-col items-center py-2 px-1 text-danger-600 bg-danger-50 rounded-lg">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="layout-dashboard" className="lucide lucide-layout-dashboard w-5 h-5"><rect width="7" height="9" x="3" y="3" rx="1"></rect><rect width="7" height="5" x="14" y="3" rx="1"></rect><rect width="7" height="9" x="14" y="12" rx="1"></rect><rect width="7" height="5" x="3" y="16" rx="1"></rect></svg>
                <span className="text-xs mt-1 font-medium">Dashboard</span>
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
        
        // Chart.js configuration
        document.addEventListener('DOMContentLoaded', function() {
            // System Metrics Chart
            const systemMetricsCtx = document.getElementById('systemMetricsChart').getContext('2d');
            new Chart(systemMetricsCtx, {
                type: 'line',
                data: {
                    labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
                    datasets: [{
                        label: 'CPU Usage (%)',
                        data: [25, 30, 45, 65, 55, 40, 35],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4,
                        fill: false
                    }, {
                        label: 'Memory Usage (%)',
                        data: [40, 42, 48, 52, 50, 45, 43],
                        borderColor: '#22c55e',
                        backgroundColor: 'rgba(34, 197, 94, 0.1)',
                        tension: 0.4,
                        fill: false
                    }, {
                        label: 'Disk I/O (MB/s)',
                        data: [15, 18, 25, 30, 28, 22, 20],
                        borderColor: '#f59e0b',
                        backgroundColor: 'rgba(245, 158, 11, 0.1)',
                        tension: 0.4,
                        fill: false
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'top',
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });

            // Emergency Mode button
            const emergencyBtn = document.querySelector('button:has(i[data-lucide="alert-triangle"])');
            if (emergencyBtn) {
                emergencyBtn.addEventListener('click', function() {
                    if (confirm('Are you sure you want to enable Emergency Mode? This will restrict platform access.')) {
                        console.log('Emergency mode activated');
                        this.textContent = 'Emergency Mode Active';
                        this.classList.remove('bg-danger-600', 'hover:bg-danger-700');
                        this.classList.add('bg-orange-600', 'hover:bg-orange-700');
                    }
                });
            }

            // Export report functionality
            const exportBtn = document.querySelector('button:has(i[data-lucide="download"])');
            if (exportBtn) {
                exportBtn.addEventListener('click', function() {
                    console.log('Exporting admin report...');
                });
            }

            // Service status click handlers
            const serviceItems = document.querySelectorAll('.space-y-3 > div');
            serviceItems.forEach(item => {
                if (item.classList.contains('cursor-pointer')) {
                    item.addEventListener('click', function() {
                        const serviceName = this.querySelector('span').textContent;
                        console.log('View service details:', serviceName);
                    });
                }
            });

            // Real-time updates simulation
            setInterval(() => {
                // Update platform health randomly
                const healthElement = document.querySelector('.text-success-600');
                if (healthElement && healthElement.textContent.includes('%')) {
                    const currentValue = parseFloat(healthElement.textContent);
                    const newValue = (currentValue + (Math.random() - 0.5) * 0.1).toFixed(1);
                    if (newValue >= 99.0 && newValue <= 100.0) {
                        healthElement.textContent = newValue + '%';
                    }
                }

                // Update API calls counter
                const apiCallsElement = document.querySelector('.text-2xl.font-bold.text-gray-900');
                if (apiCallsElement && apiCallsElement.textContent.includes('M')) {
                    const currentValue = parseFloat(apiCallsElement.textContent);
                    const increment = Math.random() * 0.01;
                    const newValue = (currentValue + increment).toFixed(1);
                    apiCallsElement.textContent = newValue + 'M';
                }
            }, 10000);

            // Alert management
            const alertItems = document.querySelectorAll('.bg-danger-50, .bg-warning-50');
            alertItems.forEach(alert => {
                alert.addEventListener('click', function() {
                    const alertTitle = this.querySelector('.font-medium').textContent;
                    console.log('View alert details:', alertTitle);
                });
            });

            // Infrastructure status management
            const infraItems = document.querySelectorAll('.bg-gray-50.rounded-lg');
            infraItems.forEach(item => {
                item.addEventListener('click', function() {
                    const infraName = this.querySelector('.font-medium').textContent;
                    console.log('Manage infrastructure:', infraName);
                });
            });

            // Time range selector for metrics
            const timeRangeSelect = document.querySelector('select');
            if (timeRangeSelect) {
                timeRangeSelect.addEventListener('change', function() {
                    const selectedRange = this.value;
                    console.log('Time range changed to:', selectedRange);
                    // Update chart data based on selected time range
                });
            }
        });
    </script>


    </div>
  );
};

export default Untitled1;