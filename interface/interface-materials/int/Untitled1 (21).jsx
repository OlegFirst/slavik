import React from 'react';

const Untitled1 = () => {
  return (
    <div>
      
    
    <nav className="bg-white border-b border-gray-200 px-4 py-3 sm:px-6">
        <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="shield-check" className="lucide lucide-shield-check w-6 h-6 text-white"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"></path><path d="m9 12 2 2 4-4"></path></svg>
                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-gray-900">AI-Platform-ISO</h1>
                        <p className="text-xs text-gray-500">Business Continuity Management</p>
                    </div>
                </div>
            </div>
            <div className="flex items-center space-x-3">
                <button className="relative p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bell" className="lucide lucide-bell w-5 h-5"><path d="M10.268 21a2 2 0 0 0 3.464 0"></path><path d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326"></path></svg>
                    <span className="absolute -top-1 -right-1 w-3 h-3 bg-danger-500 rounded-full flex items-center justify-center">
                        <span className="w-1.5 h-1.5 bg-white rounded-full"></span>
                    </span>
                </button>
                <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bot" className="lucide lucide-bot w-5 h-5"><path d="M12 8V4H8"></path><rect width="16" height="12" x="4" y="8" rx="2"></rect><path d="M2 14h2"></path><path d="M20 14h2"></path><path d="M15 13v2"></path><path d="M9 13v2"></path></svg>
                </button>
                <div className="flex items-center space-x-3 pl-3 border-l border-gray-200">
                    <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                        <span className="text-sm font-medium text-primary-600">AJ</span>
                    </div>
                    <div className="hidden md:block">
                        <p className="text-sm font-medium text-gray-900">Alex Johnson</p>
                        <p className="text-xs text-gray-500">BCM Manager</p>
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
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="home" className="lucide lucide-home text-gray-400 mr-3 h-5 w-5"><path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"></path><path d="M3 10a2 2 0 0 1 .709-1.528l7-6a2 2 0 0 1 2.582 0l7 6A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path></svg>
                            Dashboard
                        </a>
                        <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bar-chart-3" className="lucide lucide-bar-chart-3 text-gray-400 mr-3 h-5 w-5"><path d="M3 3v16a2 2 0 0 0 2 2h16"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>
                            Business Impact Analysis
                        </a>
                        <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="alert-triangle" className="lucide lucide-alert-triangle text-gray-400 mr-3 h-5 w-5"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>
                            Risk Management
                        </a>
                        <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="clipboard-list" className="lucide lucide-clipboard-list text-gray-400 mr-3 h-5 w-5"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"></rect><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><path d="M12 11h4"></path><path d="M12 16h4"></path><path d="M8 11h.01"></path><path d="M8 16h.01"></path></svg>
                            BC Plans
                        </a>
                        <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="play-circle" className="lucide lucide-play-circle text-gray-400 mr-3 h-5 w-5"><path d="M9 9.003a1 1 0 0 1 1.517-.859l4.997 2.997a1 1 0 0 1 0 1.718l-4.997 2.997A1 1 0 0 1 9 14.996z"></path><circle cx="12" cy="12" r="10"></circle></svg>
                            Exercises &amp; Testing
                        </a>
                        <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check-circle" className="lucide lucide-check-circle text-gray-400 mr-3 h-5 w-5"><path d="M21.801 10A10 10 0 1 1 17 3.335"></path><path d="m9 11 3 3L22 4"></path></svg>
                            Compliance
                        </a>
                        <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="file-text" className="lucide lucide-file-text text-gray-400 mr-3 h-5 w-5"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"></path><path d="M14 2v4a2 2 0 0 0 2 2h4"></path><path d="M10 9H8"></path><path d="M16 13H8"></path><path d="M16 17H8"></path></svg>
                            Documents
                        </a>
                        <a href="#" className="bg-primary-50 text-primary-700 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="activity" className="lucide lucide-activity text-primary-500 mr-3 h-5 w-5"><path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2"></path></svg>
                            Monitoring
                        </a>
                    </nav>
                </div>
            </div>
        </aside>

        
        <main className="flex-1 overflow-y-auto">
            <div className="py-6">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    
                    <div className="mb-8">
                        <nav className="flex mb-3" aria-label="Breadcrumb">
                            <ol className="flex items-center space-x-2 text-sm text-gray-500">
                                <li><a href="#" className="hover:text-gray-700">Dashboard</a></li>
                                <li><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="chevron-right" className="lucide lucide-chevron-right w-4 h-4"><path d="m9 18 6-6-6-6"></path></svg></li>
                                <li className="text-gray-900 font-medium">Monitoring &amp; Analytics</li>
                            </ol>
                        </nav>
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900">Monitoring &amp; Analytics</h1>
                                <p className="mt-1 text-sm text-gray-500">Real-time system monitoring and performance analytics</p>
                            </div>
                            <div className="mt-4 sm:mt-0 flex space-x-3">
                                <select className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500">
                                    <option>Last 24 hours</option>
                                    <option>Last 7 days</option>
                                    <option>Last 30 days</option>
                                    <option>Last 90 days</option>
                                </select>
                                <button className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="download" className="lucide lucide-download w-4 h-4 mr-2"><path d="M12 15V3"></path><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><path d="m7 10 5 5 5-5"></path></svg>
                                    Export Report
                                </button>
                                <button className="bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="refresh-cw" className="lucide lucide-refresh-cw w-4 h-4 mr-2"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"></path><path d="M21 3v5h-5"></path><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"></path><path d="M8 16H3v5"></path></svg>
                                    Refresh
                                </button>
                            </div>
                        </div>
                    </div>

                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                        
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">System Health</p>
                                    <p className="text-2xl font-bold text-success-600">99.7%</p>
                                    <p className="text-xs text-gray-500 mt-1">All systems operational</p>
                                </div>
                                <div className="w-12 h-12 bg-success-100 rounded-full flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check-circle" className="lucide lucide-check-circle w-6 h-6 text-success-600"><path d="M21.801 10A10 10 0 1 1 17 3.335"></path><path d="m9 11 3 3L22 4"></path></svg>
                                </div>
                            </div>
                        </div>

                        
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Active Services</p>
                                    <p className="text-2xl font-bold text-gray-900">23/23</p>
                                    <p className="text-xs text-success-600 mt-1">+0 from yesterday</p>
                                </div>
                                <div className="w-12 h-12 bg-primary-100 rounded-full flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="server" className="lucide lucide-server w-6 h-6 text-primary-600"><rect width="20" height="8" x="2" y="2" rx="2" ry="2"></rect><rect width="20" height="8" x="2" y="14" rx="2" ry="2"></rect><line x1="6" x2="6.01" y1="6" y2="6"></line><line x1="6" x2="6.01" y1="18" y2="18"></line></svg>
                                </div>
                            </div>
                        </div>

                        
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">API Requests</p>
                                    <p className="text-2xl font-bold text-gray-900">1.2M</p>
                                    <p className="text-xs text-success-600 mt-1">+12% from yesterday</p>
                                </div>
                                <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="zap" className="lucide lucide-zap w-6 h-6 text-blue-600"><path d="M4 14a1 1 0 0 1-.78-1.63l9.9-10.2a.5.5 0 0 1 .86.46l-1.92 6.02A1 1 0 0 0 13 10h7a1 1 0 0 1 .78 1.63l-9.9 10.2a.5.5 0 0 1-.86-.46l1.92-6.02A1 1 0 0 0 11 14z"></path></svg>
                                </div>
                            </div>
                        </div>

                        
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Avg Response Time</p>
                                    <p className="text-2xl font-bold text-gray-900">245ms</p>
                                    <p className="text-xs text-success-600 mt-1">-15ms from yesterday</p>
                                </div>
                                <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="clock" className="lucide lucide-clock w-6 h-6 text-green-600"><path d="M12 6v6l4 2"></path><circle cx="12" cy="12" r="10"></circle></svg>
                                </div>
                            </div>
                        </div>
                    </div>

                    
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                        
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-lg font-semibold text-gray-900">System Performance</h3>
                                <div className="flex items-center space-x-2">
                                    <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-success-100 text-success-800">
                                        <span className="w-2 h-2 bg-success-500 rounded-full mr-1"></span>
                                        Healthy
                                    </span>
                                </div>
                            </div>
                            <div className="h-80 overflow-hidden">
                                <canvas id="performanceChart" className="w-full h-full" width="988" height="640" style={{display: 'block', boxSizing: 'border-box', height: '320px', width: '494px'}}></canvas>
                            </div>
                        </div>

                        
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-lg font-semibold text-gray-900">API Response Times</h3>
                                <select className="text-sm border border-gray-300 rounded px-2 py-1">
                                    <option>Last 24h</option>
                                    <option>Last 7d</option>
                                    <option>Last 30d</option>
                                </select>
                            </div>
                            <div className="h-80 overflow-hidden">
                                <canvas id="responseTimeChart" className="w-full h-full" width="988" height="640" style={{display: 'block', boxSizing: 'border-box', height: '320px', width: '494px'}}></canvas>
                            </div>
                        </div>
                    </div>

                    
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                        
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">Platform Services</h3>
                            <div className="space-y-3">
                                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <span className="text-sm font-medium text-gray-900">API Gateway</span>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm text-gray-600">99.9%</p>
                                        <p className="text-xs text-gray-500">:8000</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <span className="text-sm font-medium text-gray-900">Auth Service</span>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm text-gray-600">100%</p>
                                        <p className="text-xs text-gray-500">:8001</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <span className="text-sm font-medium text-gray-900">User Service</span>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm text-gray-600">99.8%</p>
                                        <p className="text-xs text-gray-500">:8002</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-warning-500 rounded-full"></div>
                                        <span className="text-sm font-medium text-gray-900">Notification Service</span>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm text-gray-600">95.2%</p>
                                        <p className="text-xs text-gray-500">:8003</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <span className="text-sm font-medium text-gray-900">File Service</span>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm text-gray-600">99.7%</p>
                                        <p className="text-xs text-gray-500">:8004</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">Intelligent Core</h3>
                            <div className="space-y-3">
                                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <span className="text-sm font-medium text-gray-900">AI Orchestrator</span>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm text-gray-600">99.5%</p>
                                        <p className="text-xs text-gray-500">:9000</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <span className="text-sm font-medium text-gray-900">BIA Specialist</span>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm text-gray-600">100%</p>
                                        <p className="text-xs text-gray-500">:9001</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <span className="text-sm font-medium text-gray-900">Risk Specialist</span>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm text-gray-600">99.9%</p>
                                        <p className="text-xs text-gray-500">:9002</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <span className="text-sm font-medium text-gray-900">Plan Specialist</span>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm text-gray-600">98.7%</p>
                                        <p className="text-xs text-gray-500">:9003</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <span className="text-sm font-medium text-gray-900">RAG Engine</span>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm text-gray-600">99.8%</p>
                                        <p className="text-xs text-gray-500">:9010</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <h3 className="text-lg font-semibold text-gray-900 mb-4">Infrastructure</h3>
                            <div className="space-y-3">
                                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <span className="text-sm font-medium text-gray-900">PostgreSQL</span>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm text-gray-600">Healthy</p>
                                        <p className="text-xs text-gray-500">45/100 conn</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <span className="text-sm font-medium text-gray-900">Redis</span>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm text-gray-600">Healthy</p>
                                        <p className="text-xs text-gray-500">2.1GB used</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <span className="text-sm font-medium text-gray-900">RabbitMQ</span>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm text-gray-600">Healthy</p>
                                        <p className="text-xs text-gray-500">12 queues</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <span className="text-sm font-medium text-gray-900">Qdrant</span>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm text-gray-600">Healthy</p>
                                        <p className="text-xs text-gray-500">1.2M vectors</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-3 h-3 bg-success-500 rounded-full"></div>
                                        <span className="text-sm font-medium text-gray-900">Prometheus</span>
                                    </div>
                                    <div className="text-right">
                                        <p className="text-sm text-gray-600">Healthy</p>
                                        <p className="text-xs text-gray-500">23 targets</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-lg font-semibold text-gray-900">Recent Events</h3>
                                <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">View All</button>
                            </div>
                            <div className="space-y-3 max-h-96 overflow-y-auto">
                                <div className="flex items-start space-x-3 p-3 bg-success-50 rounded-lg">
                                    <div className="w-2 h-2 bg-success-500 rounded-full mt-2"></div>
                                    <div className="flex-1">
                                        <p className="text-sm font-medium text-gray-900">BIA Workflow Completed</p>
                                        <p className="text-xs text-gray-600">Manufacturing BIA completed successfully</p>
                                        <p className="text-xs text-gray-500 mt-1">2 minutes ago</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                                    <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                                    <div className="flex-1">
                                        <p className="text-sm font-medium text-gray-900">New Risk Identified</p>
                                        <p className="text-xs text-gray-600">AI detected potential supply chain risk</p>
                                        <p className="text-xs text-gray-500 mt-1">5 minutes ago</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-start space-x-3 p-3 bg-warning-50 rounded-lg">
                                    <div className="w-2 h-2 bg-warning-500 rounded-full mt-2"></div>
                                    <div className="flex-1">
                                        <p className="text-sm font-medium text-gray-900">Service Degradation</p>
                                        <p className="text-xs text-gray-600">Notification service experiencing delays</p>
                                        <p className="text-xs text-gray-500 mt-1">12 minutes ago</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                                    <div className="w-2 h-2 bg-gray-500 rounded-full mt-2"></div>
                                    <div className="flex-1">
                                        <p className="text-sm font-medium text-gray-900">Exercise Scheduled</p>
                                        <p className="text-xs text-gray-600">Tabletop exercise scheduled for next week</p>
                                        <p className="text-xs text-gray-500 mt-1">18 minutes ago</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-start space-x-3 p-3 bg-success-50 rounded-lg">
                                    <div className="w-2 h-2 bg-success-500 rounded-full mt-2"></div>
                                    <div className="flex-1">
                                        <p className="text-sm font-medium text-gray-900">Compliance Score Updated</p>
                                        <p className="text-xs text-gray-600">ISO 22301 compliance improved to 87%</p>
                                        <p className="text-xs text-gray-500 mt-1">25 minutes ago</p>
                                    </div>
                                </div>
                                
                                <div className="flex items-start space-x-3 p-3 bg-purple-50 rounded-lg">
                                    <div className="w-2 h-2 bg-purple-500 rounded-full mt-2"></div>
                                    <div className="flex-1">
                                        <p className="text-sm font-medium text-gray-900">AI Model Updated</p>
                                        <p className="text-xs text-gray-600">Risk prediction model retrained</p>
                                        <p className="text-xs text-gray-500 mt-1">1 hour ago</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="text-lg font-semibold text-gray-900">User Activity</h3>
                                <select className="text-sm border border-gray-300 rounded px-2 py-1">
                                    <option>Today</option>
                                    <option>This Week</option>
                                    <option>This Month</option>
                                </select>
                            </div>
                            <div className="h-80 overflow-hidden">
                                <canvas id="userActivityChart" className="w-full h-full" width="988" height="640" style={{display: 'block', boxSizing: 'border-box', height: '320px', width: '494px'}}></canvas>
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
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="home" className="lucide lucide-home w-5 h-5"><path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"></path><path d="M3 10a2 2 0 0 1 .709-1.528l7-6a2 2 0 0 1 2.582 0l7 6A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path></svg>
                <span className="text-xs mt-1">Dashboard</span>
            </button>
            <button className="flex flex-col items-center py-2 px-1 text-gray-400 hover:text-gray-600">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bar-chart-3" className="lucide lucide-bar-chart-3 w-5 h-5"><path d="M3 3v16a2 2 0 0 0 2 2h16"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>
                <span className="text-xs mt-1">BIA</span>
            </button>
            <button className="flex flex-col items-center py-2 px-1 text-gray-400 hover:text-gray-600">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="alert-triangle" className="lucide lucide-alert-triangle w-5 h-5"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>
                <span className="text-xs mt-1">Risks</span>
            </button>
            <button className="flex flex-col items-center py-2 px-1 text-gray-400 hover:text-gray-600">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="clipboard-list" className="lucide lucide-clipboard-list w-5 h-5"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"></rect><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><path d="M12 11h4"></path><path d="M12 16h4"></path><path d="M8 11h.01"></path><path d="M8 16h.01"></path></svg>
                <span className="text-xs mt-1">Plans</span>
            </button>
            <button className="flex flex-col items-center py-2 px-1 text-primary-600 bg-primary-50 rounded-lg">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="activity" className="lucide lucide-activity w-5 h-5"><path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2"></path></svg>
                <span className="text-xs mt-1 font-medium">Monitor</span>
            </button>
        </div>
    </div>

    <script>
        // Initialize Lucide icons
        lucide.createIcons();
        
        // Chart.js configurations
        document.addEventListener('DOMContentLoaded', function() {
            // System Performance Chart
            const performanceCtx = document.getElementById('performanceChart').getContext('2d');
            new Chart(performanceCtx, {
                type: 'line',
                data: {
                    labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
                    datasets: [{
                        label: 'CPU Usage (%)',
                        data: [25, 30, 45, 65, 55, 40, 35],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        tension: 0.4,
                        fill: true
                    }, {
                        label: 'Memory Usage (%)',
                        data: [40, 42, 48, 52, 50, 45, 43],
                        borderColor: '#22c55e',
                        backgroundColor: 'rgba(34, 197, 94, 0.1)',
                        tension: 0.4,
                        fill: true
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

            // API Response Time Chart
            const responseTimeCtx = document.getElementById('responseTimeChart').getContext('2d');
            new Chart(responseTimeCtx, {
                type: 'bar',
                data: {
                    labels: ['Auth', 'User', 'BIA', 'Risk', 'Plans', 'Files', 'AI'],
                    datasets: [{
                        label: 'Response Time (ms)',
                        data: [120, 180, 250, 200, 300, 150, 400],
                        backgroundColor: [
                            '#22c55e',
                            '#22c55e', 
                            '#f59e0b',
                            '#22c55e',
                            '#ef4444',
                            '#22c55e',
                            '#ef4444'
                        ],
                        borderRadius: 4
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            display: false
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            title: {
                                display: true,
                                text: 'Response Time (ms)'
                            }
                        }
                    }
                }
            });

            // User Activity Chart
            const userActivityCtx = document.getElementById('userActivityChart').getContext('2d');
            new Chart(userActivityCtx, {
                type: 'doughnut',
                data: {
                    labels: ['BIA Module', 'Risk Management', 'BC Plans', 'Compliance', 'Documents', 'Other'],
                    datasets: [{
                        data: [35, 25, 20, 10, 7, 3],
                        backgroundColor: [
                            '#3b82f6',
                            '#ef4444',
                            '#22c55e',
                            '#f59e0b',
                            '#8b5cf6',
                            '#6b7280'
                        ],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom',
                            labels: {
                                padding: 20,
                                usePointStyle: true
                            }
                        }
                    }
                }
            });

            // Auto-refresh functionality
            const refreshBtn = document.querySelector('button:has(i[data-lucide="refresh-cw"])');
            if (refreshBtn) {
                refreshBtn.addEventListener('click', function() {
                    const icon = this.querySelector('i');
                    icon.classList.add('animate-spin');
                    
                    // Simulate refresh
                    setTimeout(() => {
                        icon.classList.remove('animate-spin');
                        console.log('Data refreshed');
                    }, 1000);
                });
            }

            // Export report functionality
            const exportBtn = document.querySelector('button:has(i[data-lucide="download"])');
            if (exportBtn) {
                exportBtn.addEventListener('click', function() {
                    console.log('Exporting monitoring report...');
                });
            }

            // Time range selector
            const timeRangeSelect = document.querySelector('select');
            if (timeRangeSelect) {
                timeRangeSelect.addEventListener('change', function() {
                    const selectedRange = this.value;
                    console.log('Time range changed to:', selectedRange);
                    // Update charts based on selected time range
                });
            }

            // Service status click handlers
            const serviceItems = document.querySelectorAll('.space-y-3 > div');
            serviceItems.forEach(item => {
                item.addEventListener('click', function() {
                    const serviceName = this.querySelector('span').textContent;
                    console.log('View details for service:', serviceName);
                });
            });

            // Real-time updates simulation
            setInterval(() => {
                // Update some metrics randomly
                const healthPercentage = document.querySelector('.text-success-600');
                if (healthPercentage) {
                    const currentValue = parseFloat(healthPercentage.textContent);
                    const newValue = (currentValue + (Math.random() - 0.5) * 0.2).toFixed(1);
                    if (newValue >= 99.0 && newValue <= 100.0) {
                        healthPercentage.textContent = newValue + '%';
                    }
                }
            }, 5000);
        });
    </script>


    </div>
  );
};

export default Untitled1;