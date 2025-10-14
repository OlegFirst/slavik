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
                        <a href="#" className="bg-gray-100 text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="home" className="lucide lucide-home text-gray-500 mr-3 h-5 w-5"><path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"></path><path d="M3 10a2 2 0 0 1 .709-1.528l7-6a2 2 0 0 1 2.582 0l7 6A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path></svg>
                            Dashboard
                        </a>
                        <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bar-chart-3" className="lucide lucide-bar-chart-3 text-gray-400 mr-3 h-5 w-5"><path d="M3 3v16a2 2 0 0 0 2 2h16"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>
                            Business Impact Analysis
                        </a>
                        <a href="#" className="bg-primary-50 text-primary-700 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="alert-triangle" className="lucide lucide-alert-triangle text-primary-500 mr-3 h-5 w-5"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>
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
                        <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="activity" className="lucide lucide-activity text-gray-400 mr-3 h-5 w-5"><path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2"></path></svg>
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
                                <li className="text-gray-900 font-medium">Risk Management</li>
                            </ol>
                        </nav>
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900">Risk Management</h1>
                                <p className="mt-1 text-sm text-gray-500">Identify, assess, and manage organizational risks</p>
                            </div>
                            <div className="mt-4 sm:mt-0 flex space-x-3">
                                <button className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="download" className="lucide lucide-download w-4 h-4 mr-2"><path d="M12 15V3"></path><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><path d="m7 10 5 5 5-5"></path></svg>
                                    Export Register
                                </button>
                                <button className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bot" className="lucide lucide-bot w-4 h-4 mr-2"><path d="M12 8V4H8"></path><rect width="16" height="12" x="4" y="8" rx="2"></rect><path d="M2 14h2"></path><path d="M20 14h2"></path><path d="M15 13v2"></path><path d="M9 13v2"></path></svg>
                                    AI Analysis
                                </button>
                                <button className="bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="plus" className="lucide lucide-plus w-4 h-4 mr-2"><path d="M5 12h14"></path><path d="M12 5v14"></path></svg>
                                    Add Risk
                                </button>
                            </div>
                        </div>
                    </div>

                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Total Risks</p>
                                    <p className="text-2xl font-bold text-gray-900">47</p>
                                </div>
                                <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="alert-triangle" className="lucide lucide-alert-triangle w-6 h-6 text-gray-600"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>
                                </div>
                            </div>
                            <div className="mt-4 flex items-center text-sm">
                                <span className="text-success-600 flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="trending-up" className="lucide lucide-trending-up w-4 h-4 mr-1"><path d="M16 7h6v6"></path><path d="m22 7-8.5 8.5-5-5L2 17"></path></svg>
                                    +3 this month
                                </span>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Critical Risks</p>
                                    <p className="text-2xl font-bold text-danger-600">8</p>
                                </div>
                                <div className="w-12 h-12 bg-danger-100 rounded-lg flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="alert-circle" className="lucide lucide-alert-circle w-6 h-6 text-danger-600"><circle cx="12" cy="12" r="10"></circle><line x1="12" x2="12" y1="8" y2="12"></line><line x1="12" x2="12.01" y1="16" y2="16"></line></svg>
                                </div>
                            </div>
                            <div className="mt-4 flex items-center text-sm">
                                <span className="text-danger-600 flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="trending-up" className="lucide lucide-trending-up w-4 h-4 mr-1"><path d="M16 7h6v6"></path><path d="m22 7-8.5 8.5-5-5L2 17"></path></svg>
                                    +2 this week
                                </span>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">In Treatment</p>
                                    <p className="text-2xl font-bold text-warning-600">23</p>
                                </div>
                                <div className="w-12 h-12 bg-warning-100 rounded-lg flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="wrench" className="lucide lucide-wrench w-6 h-6 text-warning-600"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.106-3.105c.32-.322.863-.22.983.218a6 6 0 0 1-8.259 7.057l-7.91 7.91a1 1 0 0 1-2.999-3l7.91-7.91a6 6 0 0 1 7.057-8.259c.438.12.54.662.219.984z"></path></svg>
                                </div>
                            </div>
                            <div className="mt-4 flex items-center text-sm">
                                <span className="text-success-600 flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="trending-down" className="lucide lucide-trending-down w-4 h-4 mr-1"><path d="M16 17h6v-6"></path><path d="m22 17-8.5-8.5-5 5L2 7"></path></svg>
                                    -5 this month
                                </span>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Risk Score</p>
                                    <p className="text-2xl font-bold text-warning-600">7.2</p>
                                </div>
                                <div className="w-12 h-12 bg-warning-100 rounded-lg flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="gauge" className="lucide lucide-gauge w-6 h-6 text-warning-600"><path d="m12 14 4-4"></path><path d="M3.34 19a10 10 0 1 1 17.32 0"></path></svg>
                                </div>
                            </div>
                            <div className="mt-4 flex items-center text-sm">
                                <span className="text-success-600 flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="trending-down" className="lucide lucide-trending-down w-4 h-4 mr-1"><path d="M16 17h6v-6"></path><path d="m22 17-8.5-8.5-5 5L2 7"></path></svg>
                                    -0.3 this month
                                </span>
                            </div>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
                        
                        <div className="xl:col-span-2">
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                                <div className="p-6 border-b border-gray-200">
                                    <div className="flex items-center justify-between">
                                        <h2 className="text-lg font-semibold text-gray-900">Risk Heatmap</h2>
                                        <div className="flex items-center space-x-2">
                                            <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="maximize-2" className="lucide lucide-maximize-2 w-4 h-4"><path d="M15 3h6v6"></path><path d="m21 3-7 7"></path><path d="m3 21 7-7"></path><path d="M9 21H3v-6"></path></svg>
                                            </button>
                                            <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="download" className="lucide lucide-download w-4 h-4"><path d="M12 15V3"></path><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><path d="m7 10 5 5 5-5"></path></svg>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                                <div className="p-6">
                                    
                                    <div className="relative">
                                        
                                        <div className="absolute -left-16 top-1/2 transform -translate-y-1/2 -rotate-90">
                                            <span className="text-sm font-medium text-gray-700">Likelihood</span>
                                        </div>
                                        
                                        
                                        <div className="absolute -left-8 top-0 h-full flex flex-col justify-between text-xs text-gray-500 py-4">
                                            <span>5</span>
                                            <span>4</span>
                                            <span>3</span>
                                            <span>2</span>
                                            <span>1</span>
                                        </div>
                                        
                                        
                                        <div className="grid grid-cols-5 gap-1 h-80 ml-4">
                                            
                                            <div className="bg-warning-200 rounded border-2 border-warning-300 relative group cursor-pointer hover:border-warning-500 transition-colors flex items-center justify-center">
                                                <div className="w-3 h-3 bg-warning-600 rounded-full" title="Risk R-001"></div>
                                                <div className="absolute bottom-2 left-2 text-xs font-medium text-warning-800">2</div>
                                            </div>
                                            <div className="bg-warning-300 rounded border-2 border-warning-400 relative group cursor-pointer hover:border-warning-600 transition-colors flex items-center justify-center">
                                                <div className="w-3 h-3 bg-warning-700 rounded-full mr-1" title="Risk R-002"></div>
                                                <div className="w-3 h-3 bg-warning-700 rounded-full" title="Risk R-003"></div>
                                                <div className="absolute bottom-2 left-2 text-xs font-medium text-warning-900">3</div>
                                            </div>
                                            <div className="bg-danger-200 rounded border-2 border-danger-300 relative group cursor-pointer hover:border-danger-500 transition-colors flex items-center justify-center">
                                                <div className="w-3 h-3 bg-danger-600 rounded-full mr-1" title="Risk R-004"></div>
                                                <div className="w-3 h-3 bg-danger-600 rounded-full" title="Risk R-005"></div>
                                                <div className="absolute bottom-2 left-2 text-xs font-medium text-danger-800">4</div>
                                            </div>
                                            <div className="bg-danger-400 rounded border-2 border-danger-500 relative group cursor-pointer hover:border-danger-700 transition-colors flex items-center justify-center">
                                                <div className="w-3 h-3 bg-danger-800 rounded-full mr-1" title="Risk R-006"></div>
                                                <div className="w-3 h-3 bg-danger-800 rounded-full" title="Risk R-007"></div>
                                                <div className="absolute bottom-2 left-2 text-xs font-medium text-white">2</div>
                                            </div>
                                            <div className="bg-danger-600 rounded border-2 border-danger-700 relative group cursor-pointer hover:border-danger-800 transition-colors flex items-center justify-center">
                                                <div className="w-3 h-3 bg-white rounded-full" title="Risk R-008"></div>
                                                <div className="absolute bottom-2 left-2 text-xs font-medium text-white">1</div>
                                            </div>
                                            
                                            
                                            <div className="bg-success-200 rounded border-2 border-success-300 relative group cursor-pointer hover:border-success-500 transition-colors flex items-center justify-center">
                                                <div className="w-3 h-3 bg-success-600 rounded-full mr-1" title="Risk R-009"></div>
                                                <div className="w-3 h-3 bg-success-600 rounded-full" title="Risk R-010"></div>
                                                <div className="absolute bottom-2 left-2 text-xs font-medium text-success-800">3</div>
                                            </div>
                                            <div className="bg-warning-200 rounded border-2 border-warning-300 relative group cursor-pointer hover:border-warning-500 transition-colors flex items-center justify-center">
                                                <div className="w-3 h-3 bg-warning-600 rounded-full mr-1" title="Risk R-011"></div>
                                                <div className="w-3 h-3 bg-warning-600 rounded-full mr-1" title="Risk R-012"></div>
                                                <div className="w-3 h-3 bg-warning-600 rounded-full" title="Risk R-013"></div>
                                                <div className="absolute bottom-2 left-2 text-xs font-medium text-warning-800">5</div>
                                            </div>
                                            <div className="bg-warning-300 rounded border-2 border-warning-400 relative group cursor-pointer hover:border-warning-600 transition-colors flex items-center justify-center">
                                                <div className="w-3 h-3 bg-warning-700 rounded-full mr-1" title="Risk R-014"></div>
                                                <div className="w-3 h-3 bg-warning-700 rounded-full" title="Risk R-015"></div>
                                                <div className="absolute bottom-2 left-2 text-xs font-medium text-warning-900">4</div>
                                            </div>
                                            <div className="bg-danger-300 rounded border-2 border-danger-400 relative group cursor-pointer hover:border-danger-600 transition-colors flex items-center justify-center">
                                                <div className="w-3 h-3 bg-danger-700 rounded-full mr-1" title="Risk R-016"></div>
                                                <div className="w-3 h-3 bg-danger-700 rounded-full" title="Risk R-017"></div>
                                                <div className="absolute bottom-2 left-2 text-xs font-medium text-danger-900">3</div>
                                            </div>
                                            <div className="bg-danger-500 rounded border-2 border-danger-600 relative group cursor-pointer hover:border-danger-700 transition-colors flex items-center justify-center">
                                                <div className="w-3 h-3 bg-white rounded-full" title="Risk R-018"></div>
                                                <div className="absolute bottom-2 left-2 text-xs font-medium text-white">1</div>
                                            </div>
                                            
                                            
                                            <div className="bg-success-100 rounded border-2 border-success-200 relative group cursor-pointer hover:border-success-400 transition-colors flex items-center justify-center">
                                                <div className="w-3 h-3 bg-success-500 rounded-full mr-1" title="Risk R-019"></div>
                                                <div className="w-3 h-3 bg-success-500 rounded-full mr-1" title="Risk R-020"></div>
                                                <div className="w-3 h-3 bg-success-500 rounded-full" title="Risk R-021"></div>
                                                <div className="absolute bottom-2 left-2 text-xs font-medium text-success-700">4</div>
                                            </div>
                                            <div className="bg-success-200 rounded border-2 border-success-300 relative group cursor-pointer hover:border-success-500 transition-colors flex items-center justify-center">
                                                <div className="w-3 h-3 bg-success-600 rounded-full mr-1" title="Risk R-022"></div>
                                                <div className="w-3 h-3 bg-success-600 rounded-full mr-1" title="Risk R-023"></div>
                                                <div className="w-3 h-3 bg-success-600 rounded-full" title="Risk R-024"></div>
                                                <div className="absolute bottom-2 left-2 text-xs font-medium text-success-800">6</div>
                                            </div>
                                            <div className="bg-warning-200 rounded border-2 border-warning-300 relative group cursor-pointer hover:border-warning-500 transition-colors flex items-center justify-center">
                                                <div className="w-3 h-3 bg-warning-600 rounded-full mr-1" title="Risk R-025"></div>
                                                <div className="w-3 h-3 bg-warning-600 rounded-full" title="Risk R-026"></div>
                                                <div className="absolute bottom-2 left-2 text-xs font-medium text-warning-800">3</div>
                                            </div>
                                            <div className="bg-warning-300 rounded border-2 border-warning-400 relative group cursor-pointer hover:border-warning-600 transition-colors flex items-center justify-center">
                                                <div className="w-3 h-3 bg-warning-700 rounded-full mr-1" title="Risk R-027"></div>
                                                <div className="w-3 h-3 bg-warning-700 rounded-full" title="Risk R-028"></div>
                                                <div className="absolute bottom-2 left-2 text-xs font-medium text-warning-900">2</div>
                                            </div>
                                            <div className="bg-danger-300 rounded border-2 border-danger-400 relative group cursor-pointer hover:border-danger-600 transition-colors flex items-center justify-center">
                                                <div className="w-3 h-3 bg-danger-700 rounded-full" title="Risk R-029"></div>
                                                <div className="absolute bottom-2 left-2 text-xs font-medium text-danger-900">1</div>
                                            </div>
                                            
                                            
                                            <div className="bg-success-50 rounded border-2 border-success-100 relative group cursor-pointer hover:border-success-300 transition-colors flex items-center justify-center">
                                                <div className="w-3 h-3 bg-success-400 rounded-full mr-1" title="Risk R-030"></div>
                                                <div className="w-3 h-3 bg-success-400 rounded-full mr-1" title="Risk R-031"></div>
                                                <div className="w-3 h-3 bg-success-400 rounded-full" title="Risk R-032"></div>
                                                <div className="absolute bottom-2 left-2 text-xs font-medium text-success-600">5</div>
                                            </div>
                                            <div className="bg-success-100 rounded border-2 border-success-200 relative group cursor-pointer hover:border-success-400 transition-colors flex items-center justify-center">
                                                <div className="w-3 h-3 bg-success-500 rounded-full mr-1" title="Risk R-033"></div>
                                                <div className="w-3 h-3 bg-success-500 rounded-full" title="Risk R-034"></div>
                                                <div className="absolute bottom-2 left-2 text-xs font-medium text-success-700">4</div>
                                            </div>
                                            <div className="bg-success-200 rounded border-2 border-success-300 relative group cursor-pointer hover:border-success-500 transition-colors flex items-center justify-center">
                                                <div className="w-3 h-3 bg-success-600 rounded-full mr-1" title="Risk R-035"></div>
                                                <div className="w-3 h-3 bg-success-600 rounded-full" title="Risk R-036"></div>
                                                <div className="absolute bottom-2 left-2 text-xs font-medium text-success-800">3</div>
                                            </div>
                                            <div className="bg-warning-200 rounded border-2 border-warning-300 relative group cursor-pointer hover:border-warning-500 transition-colors flex items-center justify-center">
                                                <div className="w-3 h-3 bg-warning-600 rounded-full" title="Risk R-037"></div>
                                                <div className="absolute bottom-2 left-2 text-xs font-medium text-warning-800">2</div>
                                            </div>
                                            <div className="bg-warning-300 rounded border-2 border-warning-400 relative group cursor-pointer hover:border-warning-600 transition-colors flex items-center justify-center">
                                                <div className="w-3 h-3 bg-warning-700 rounded-full" title="Risk R-038"></div>
                                                <div className="absolute bottom-2 left-2 text-xs font-medium text-warning-900">1</div>
                                            </div>
                                            
                                            
                                            <div className="bg-gray-50 rounded border-2 border-gray-100 relative group cursor-pointer hover:border-gray-300 transition-colors flex items-center justify-center">
                                                <div className="w-3 h-3 bg-gray-400 rounded-full mr-1" title="Risk R-039"></div>
                                                <div className="w-3 h-3 bg-gray-400 rounded-full mr-1" title="Risk R-040"></div>
                                                <div className="w-3 h-3 bg-gray-400 rounded-full" title="Risk R-041"></div>
                                                <div className="absolute bottom-2 left-2 text-xs font-medium text-gray-600">6</div>
                                            </div>
                                            <div className="bg-success-50 rounded border-2 border-success-100 relative group cursor-pointer hover:border-success-300 transition-colors flex items-center justify-center">
                                                <div className="w-3 h-3 bg-success-400 rounded-full mr-1" title="Risk R-042"></div>
                                                <div className="w-3 h-3 bg-success-400 rounded-full" title="Risk R-043"></div>
                                                <div className="absolute bottom-2 left-2 text-xs font-medium text-success-600">3</div>
                                            </div>
                                            <div className="bg-success-100 rounded border-2 border-success-200 relative group cursor-pointer hover:border-success-400 transition-colors flex items-center justify-center">
                                                <div className="w-3 h-3 bg-success-500 rounded-full mr-1" title="Risk R-044"></div>
                                                <div className="w-3 h-3 bg-success-500 rounded-full" title="Risk R-045"></div>
                                                <div className="absolute bottom-2 left-2 text-xs font-medium text-success-700">2</div>
                                            </div>
                                            <div className="bg-success-200 rounded border-2 border-success-300 relative group cursor-pointer hover:border-success-500 transition-colors flex items-center justify-center">
                                                <div className="w-3 h-3 bg-success-600 rounded-full" title="Risk R-046"></div>
                                                <div className="absolute bottom-2 left-2 text-xs font-medium text-success-800">1</div>
                                            </div>
                                            <div className="bg-warning-200 rounded border-2 border-warning-300 relative group cursor-pointer hover:border-warning-500 transition-colors flex items-center justify-center">
                                                <div className="w-3 h-3 bg-warning-600 rounded-full" title="Risk R-047"></div>
                                                <div className="absolute bottom-2 left-2 text-xs font-medium text-warning-800">1</div>
                                            </div>
                                        </div>
                                        
                                        
                                        <div className="flex justify-between text-xs text-gray-500 mt-2 ml-4">
                                            <span>1</span>
                                            <span>2</span>
                                            <span>3</span>
                                            <span>4</span>
                                            <span>5</span>
                                        </div>
                                        
                                        
                                        <div className="text-center mt-4">
                                            <span className="text-sm font-medium text-gray-700">Impact</span>
                                        </div>
                                    </div>
                                    
                                    
                                    <div className="mt-6 flex items-center justify-center space-x-6 text-xs">
                                        <div className="flex items-center space-x-2">
                                            <div className="w-4 h-4 bg-success-200 rounded border border-success-300"></div>
                                            <span className="text-gray-600">Low Risk</span>
                                        </div>
                                        <div className="flex items-center space-x-2">
                                            <div className="w-4 h-4 bg-warning-200 rounded border border-warning-300"></div>
                                            <span className="text-gray-600">Medium Risk</span>
                                        </div>
                                        <div className="flex items-center space-x-2">
                                            <div className="w-4 h-4 bg-danger-300 rounded border border-danger-400"></div>
                                            <span className="text-gray-600">High Risk</span>
                                        </div>
                                        <div className="flex items-center space-x-2">
                                            <div className="w-4 h-4 bg-danger-600 rounded border border-danger-700"></div>
                                            <span className="text-gray-600">Critical Risk</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        
                        <div className="xl:col-span-1">
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-6">
                                <div className="p-4 border-b border-gray-200">
                                    <h3 className="text-sm font-semibold text-gray-900">Filters</h3>
                                </div>
                                <div className="p-4 space-y-4">
                                    
                                    <div>
                                        <label className="block text-xs font-medium text-gray-700 mb-2">Search Risks</label>
                                        <div className="relative">
                                            <input type="text" placeholder="Search by title, ID, or owner..." className="w-full pl-8 pr-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500" />
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="search" className="lucide lucide-search absolute left-2.5 top-2.5 w-3 h-3 text-gray-400"><path d="m21 21-4.34-4.34"></path><circle cx="11" cy="11" r="8"></circle></svg>
                                        </div>
                                    </div>
                                    
                                    
                                    <div>
                                        <label className="block text-xs font-medium text-gray-700 mb-2">Category</label>
                                        <select className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500">
                                            <option value="">All Categories</option>
                                            <option value="strategic">Strategic</option>
                                            <option value="operational">Operational</option>
                                            <option value="financial">Financial</option>
                                            <option value="cyber">Cyber Security</option>
                                            <option value="compliance">Compliance</option>
                                            <option value="reputation">Reputation</option>
                                        </select>
                                    </div>
                                    
                                    
                                    <div>
                                        <label className="block text-xs font-medium text-gray-700 mb-2">Risk Level</label>
                                        <div className="space-y-2">
                                            <label className="flex items-center">
                                                <input type="checkbox" className="rounded border-gray-300 text-danger-600 focus:ring-danger-500" />
                                                <span className="ml-2 text-sm text-gray-700">Critical</span>
                                                <span className="ml-auto text-xs text-gray-500">8</span>
                                            </label>
                                            <label className="flex items-center">
                                                <input type="checkbox" className="rounded border-gray-300 text-warning-600 focus:ring-warning-500" />
                                                <span className="ml-2 text-sm text-gray-700">High</span>
                                                <span className="ml-auto text-xs text-gray-500">15</span>
                                            </label>
                                            <label className="flex items-center">
                                                <input type="checkbox" className="rounded border-gray-300 text-warning-600 focus:ring-warning-500" />
                                                <span className="ml-2 text-sm text-gray-700">Medium</span>
                                                <span className="ml-auto text-xs text-gray-500">18</span>
                                            </label>
                                            <label className="flex items-center">
                                                <input type="checkbox" className="rounded border-gray-300 text-success-600 focus:ring-success-500" />
                                                <span className="ml-2 text-sm text-gray-700">Low</span>
                                                <span className="ml-auto text-xs text-gray-500">6</span>
                                            </label>
                                        </div>
                                    </div>
                                    
                                    
                                    <div>
                                        <label className="block text-xs font-medium text-gray-700 mb-2">Status</label>
                                        <div className="space-y-2">
                                            <label className="flex items-center">
                                                <input type="checkbox" className="rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
                                                <span className="ml-2 text-sm text-gray-700">Open</span>
                                                <span className="ml-auto text-xs text-gray-500">32</span>
                                            </label>
                                            <label className="flex items-center">
                                                <input type="checkbox" className="rounded border-gray-300 text-warning-600 focus:ring-warning-500" />
                                                <span className="ml-2 text-sm text-gray-700">In Treatment</span>
                                                <span className="ml-auto text-xs text-gray-500">23</span>
                                            </label>
                                            <label className="flex items-center">
                                                <input type="checkbox" className="rounded border-gray-300 text-success-600 focus:ring-success-500" />
                                                <span className="ml-2 text-sm text-gray-700">Closed</span>
                                                <span className="ml-auto text-xs text-gray-500">12</span>
                                            </label>
                                        </div>
                                    </div>
                                    
                                    
                                    <div>
                                        <label className="block text-xs font-medium text-gray-700 mb-2">Risk Owner</label>
                                        <select className="w-full px-3 py-2 text-sm border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary-500 focus:border-primary-500">
                                            <option value="">All Owners</option>
                                            <option value="alex">Alex Johnson</option>
                                            <option value="sarah">Sarah Chen</option>
                                            <option value="mike">Mike Rodriguez</option>
                                            <option value="emma">Emma Thompson</option>
                                        </select>
                                    </div>
                                    
                                    <button className="w-full bg-gray-100 text-gray-700 px-3 py-2 rounded-lg text-sm font-medium hover:bg-gray-200 transition-colors">
                                        Clear All Filters
                                    </button>
                                </div>
                            </div>
                            
                            
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                                <div className="p-4 border-b border-gray-200">
                                    <div className="flex items-center space-x-2">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bot" className="lucide lucide-bot w-4 h-4 text-primary-600"><path d="M12 8V4H8"></path><rect width="16" height="12" x="4" y="8" rx="2"></rect><path d="M2 14h2"></path><path d="M20 14h2"></path><path d="M15 13v2"></path><path d="M9 13v2"></path></svg>
                                        <h3 className="text-sm font-semibold text-gray-900">AI Risk Insights</h3>
                                    </div>
                                </div>
                                <div className="p-4 space-y-4">
                                    <div className="p-3 bg-danger-50 rounded-lg border border-danger-200">
                                        <div className="flex items-start space-x-2">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="alert-triangle" className="lucide lucide-alert-triangle w-4 h-4 text-danger-600 mt-0.5 flex-shrink-0"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>
                                            <div>
                                                <p className="text-sm font-medium text-danger-800">Critical Risk Alert</p>
                                                <p className="text-xs text-danger-700 mt-1">3 new critical risks identified this week. Immediate attention required.</p>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div className="p-3 bg-warning-50 rounded-lg border border-warning-200">
                                        <div className="flex items-start space-x-2">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="trending-up" className="lucide lucide-trending-up w-4 h-4 text-warning-600 mt-0.5 flex-shrink-0"><path d="M16 7h6v6"></path><path d="m22 7-8.5 8.5-5-5L2 17"></path></svg>
                                            <div>
                                                <p className="text-sm font-medium text-warning-800">Risk Trend</p>
                                                <p className="text-xs text-warning-700 mt-1">Cyber security risks increasing. Consider additional controls.</p>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <div className="p-3 bg-primary-50 rounded-lg border border-primary-200">
                                        <div className="flex items-start space-x-2">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="lightbulb" className="lucide lucide-lightbulb w-4 h-4 text-primary-600 mt-0.5 flex-shrink-0"><path d="M15 14c.2-1 .7-1.7 1.5-2.5 1-.9 1.5-2.2 1.5-3.5A6 6 0 0 0 6 8c0 1 .2 2.2 1.5 3.5.7.7 1.3 1.5 1.5 2.5"></path><path d="M9 18h6"></path><path d="M10 22h4"></path></svg>
                                            <div>
                                                <p className="text-sm font-medium text-primary-800">Recommendation</p>
                                                <p className="text-xs text-primary-700 mt-1">Review treatment plans for risks R-006 and R-007.</p>
                                            </div>
                                        </div>
                                    </div>
                                    
                                    <button className="w-full bg-primary-600 text-white px-3 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors flex items-center justify-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="brain" className="lucide lucide-brain w-4 h-4 mr-2"><path d="M12 18V5"></path><path d="M15 13a4.17 4.17 0 0 1-3-4 4.17 4.17 0 0 1-3 4"></path><path d="M17.598 6.5A3 3 0 1 0 12 5a3 3 0 1 0-5.598 1.5"></path><path d="M17.997 5.125a4 4 0 0 1 2.526 5.77"></path><path d="M18 18a4 4 0 0 0 2-7.464"></path><path d="M19.967 17.483A4 4 0 1 1 12 18a4 4 0 1 1-7.967-.517"></path><path d="M6 18a4 4 0 0 1-2-7.464"></path><path d="M6.003 5.125a4 4 0 0 0-2.526 5.77"></path></svg>
                                        Get Full AI Analysis
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 mt-8">
                        <div className="p-6 border-b border-gray-200">
                            <div className="flex items-center justify-between">
                                <h2 className="text-lg font-semibold text-gray-900">Risk Register</h2>
                                <div className="flex items-center space-x-3">
                                    <div className="flex items-center space-x-2 text-sm text-gray-500">
                                        <span>Show:</span>
                                        <select className="border border-gray-300 rounded px-2 py-1 text-sm">
                                            <option>10</option>
                                            <option>25</option>
                                            <option>50</option>
                                            <option>All</option>
                                        </select>
                                    </div>
                                    <button className="bg-white border border-gray-300 text-gray-700 px-3 py-1.5 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors flex items-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="download" className="lucide lucide-download w-4 h-4 mr-1"><path d="M12 15V3"></path><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><path d="m7 10 5 5 5-5"></path></svg>
                                        Export
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div className="overflow-x-auto">
                            <table className="min-w-full divide-y divide-gray-200">
                                <thead className="bg-gray-50">
                                    <tr>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100">
                                            <div className="flex items-center space-x-1">
                                                <span>Risk ID</span>
                                                <i data-lucide="chevron-up-down" className="w-3 h-3"></i>
                                            </div>
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100">
                                            <div className="flex items-center space-x-1">
                                                <span>Risk Title</span>
                                                <i data-lucide="chevron-up-down" className="w-3 h-3"></i>
                                            </div>
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100">
                                            <div className="flex items-center space-x-1">
                                                <span>Category</span>
                                                <i data-lucide="chevron-up-down" className="w-3 h-3"></i>
                                            </div>
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100">
                                            <div className="flex items-center space-x-1">
                                                <span>Likelihood</span>
                                                <i data-lucide="chevron-up-down" className="w-3 h-3"></i>
                                            </div>
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100">
                                            <div className="flex items-center space-x-1">
                                                <span>Impact</span>
                                                <i data-lucide="chevron-up-down" className="w-3 h-3"></i>
                                            </div>
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100">
                                            <div className="flex items-center space-x-1">
                                                <span>Risk Level</span>
                                                <i data-lucide="chevron-up-down" className="w-3 h-3"></i>
                                            </div>
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100">
                                            <div className="flex items-center space-x-1">
                                                <span>Owner</span>
                                                <i data-lucide="chevron-up-down" className="w-3 h-3"></i>
                                            </div>
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100">
                                            <div className="flex items-center space-x-1">
                                                <span>Status</span>
                                                <i data-lucide="chevron-up-down" className="w-3 h-3"></i>
                                            </div>
                                        </th>
                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                                            Actions
                                        </th>
                                    </tr>
                                </thead>
                                <tbody className="bg-white divide-y divide-gray-200">
                                    <tr className="hover:bg-gray-50 cursor-pointer">
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">R-001</td>
                                        <td className="px-6 py-4 text-sm text-gray-900">
                                            <div className="max-w-xs">
                                                <p className="font-medium">Data Center Power Failure</p>
                                                <p className="text-gray-500 text-xs mt-1">Risk of complete power loss at primary data center</p>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                                                Operational
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">3</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">5</td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-danger-100 text-danger-800">
                                                Critical
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center space-x-2">
                                                <div className="w-6 h-6 bg-primary-100 rounded-full flex items-center justify-center">
                                                    <span className="text-xs font-medium text-primary-600">AJ</span>
                                                </div>
                                                <span className="text-sm text-gray-900">Alex Johnson</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-warning-100 text-warning-800">
                                                In Treatment
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                            <div className="flex items-center space-x-2">
                                                <button className="text-primary-600 hover:text-primary-900">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="eye" className="lucide lucide-eye w-4 h-4"><path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"></path><circle cx="12" cy="12" r="3"></circle></svg>
                                                </button>
                                                <button className="text-gray-400 hover:text-gray-600">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="edit" className="lucide lucide-edit w-4 h-4"><path d="M12 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.375 2.625a1 1 0 0 1 3 3l-9.013 9.014a2 2 0 0 1-.853.505l-2.873.84a.5.5 0 0 1-.62-.62l.84-2.873a2 2 0 0 1 .506-.852z"></path></svg>
                                                </button>
                                                <button className="text-gray-400 hover:text-gray-600">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="more-horizontal" className="lucide lucide-more-horizontal w-4 h-4"><circle cx="12" cy="12" r="1"></circle><circle cx="19" cy="12" r="1"></circle><circle cx="5" cy="12" r="1"></circle></svg>
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                    <tr className="hover:bg-gray-50 cursor-pointer">
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">R-002</td>
                                        <td className="px-6 py-4 text-sm text-gray-900">
                                            <div className="max-w-xs">
                                                <p className="font-medium">Cyber Security Breach</p>
                                                <p className="text-gray-500 text-xs mt-1">Unauthorized access to customer data systems</p>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                                Cyber Security
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">4</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">4</td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-danger-100 text-danger-800">
                                                High
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center space-x-2">
                                                <div className="w-6 h-6 bg-green-100 rounded-full flex items-center justify-center">
                                                    <span className="text-xs font-medium text-green-600">SC</span>
                                                </div>
                                                <span className="text-sm text-gray-900">Sarah Chen</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                                Open
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                            <div className="flex items-center space-x-2">
                                                <button className="text-primary-600 hover:text-primary-900">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="eye" className="lucide lucide-eye w-4 h-4"><path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"></path><circle cx="12" cy="12" r="3"></circle></svg>
                                                </button>
                                                <button className="text-gray-400 hover:text-gray-600">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="edit" className="lucide lucide-edit w-4 h-4"><path d="M12 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.375 2.625a1 1 0 0 1 3 3l-9.013 9.014a2 2 0 0 1-.853.505l-2.873.84a.5.5 0 0 1-.62-.62l.84-2.873a2 2 0 0 1 .506-.852z"></path></svg>
                                                </button>
                                                <button className="text-gray-400 hover:text-gray-600">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="more-horizontal" className="lucide lucide-more-horizontal w-4 h-4"><circle cx="12" cy="12" r="1"></circle><circle cx="19" cy="12" r="1"></circle><circle cx="5" cy="12" r="1"></circle></svg>
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                    <tr className="hover:bg-gray-50 cursor-pointer">
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">R-003</td>
                                        <td className="px-6 py-4 text-sm text-gray-900">
                                            <div className="max-w-xs">
                                                <p className="font-medium">Key Personnel Loss</p>
                                                <p className="text-gray-500 text-xs mt-1">Loss of critical team members without succession plan</p>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                                Strategic
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">3</td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">3</td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-warning-100 text-warning-800">
                                                Medium
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <div className="flex items-center space-x-2">
                                                <div className="w-6 h-6 bg-orange-100 rounded-full flex items-center justify-center">
                                                    <span className="text-xs font-medium text-orange-600">MR</span>
                                                </div>
                                                <span className="text-sm text-gray-900">Mike Rodriguez</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-warning-100 text-warning-800">
                                                In Treatment
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                            <div className="flex items-center space-x-2">
                                                <button className="text-primary-600 hover:text-primary-900">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="eye" className="lucide lucide-eye w-4 h-4"><path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"></path><circle cx="12" cy="12" r="3"></circle></svg>
                                                </button>
                                                <button className="text-gray-400 hover:text-gray-600">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="edit" className="lucide lucide-edit w-4 h-4"><path d="M12 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.375 2.625a1 1 0 0 1 3 3l-9.013 9.014a2 2 0 0 1-.853.505l-2.873.84a.5.5 0 0 1-.62-.62l.84-2.873a2 2 0 0 1 .506-.852z"></path></svg>
                                                </button>
                                                <button className="text-gray-400 hover:text-gray-600">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="more-horizontal" className="lucide lucide-more-horizontal w-4 h-4"><circle cx="12" cy="12" r="1"></circle><circle cx="19" cy="12" r="1"></circle><circle cx="5" cy="12" r="1"></circle></svg>
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                </tbody>
                            </table>
                        </div>
                        <div className="bg-white px-4 py-3 border-t border-gray-200 sm:px-6">
                            <div className="flex items-center justify-between">
                                <div className="flex items-center text-sm text-gray-500">
                                    <span>Showing 1 to 3 of 47 results</span>
                                </div>
                                <div className="flex items-center space-x-2">
                                    <button className="px-3 py-1 border border-gray-300 rounded text-sm text-gray-500 hover:bg-gray-50 disabled:opacity-50" disabled="">
                                        Previous
                                    </button>
                                    <button className="px-3 py-1 bg-primary-600 text-white rounded text-sm hover:bg-primary-700">
                                        1
                                    </button>
                                    <button className="px-3 py-1 border border-gray-300 rounded text-sm text-gray-700 hover:bg-gray-50">
                                        2
                                    </button>
                                    <button className="px-3 py-1 border border-gray-300 rounded text-sm text-gray-700 hover:bg-gray-50">
                                        3
                                    </button>
                                    <span className="px-2 text-gray-500">...</span>
                                    <button className="px-3 py-1 border border-gray-300 rounded text-sm text-gray-700 hover:bg-gray-50">
                                        16
                                    </button>
                                    <button className="px-3 py-1 border border-gray-300 rounded text-sm text-gray-700 hover:bg-gray-50">
                                        Next
                                    </button>
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
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="home" className="lucide lucide-home w-5 h-5"><path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"></path><path d="M3 10a2 2 0 0 1 .709-1.528l7-6a2 2 0 0 1 2.582 0l7 6A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path></svg>
                <span className="text-xs mt-1">Dashboard</span>
            </button>
            <button className="flex flex-col items-center py-2 px-1 text-gray-400 hover:text-gray-600">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bar-chart-3" className="lucide lucide-bar-chart-3 w-5 h-5"><path d="M3 3v16a2 2 0 0 0 2 2h16"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>
                <span className="text-xs mt-1">BIA</span>
            </button>
            <button className="flex flex-col items-center py-2 px-1 text-primary-600 bg-primary-50 rounded-lg">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="alert-triangle" className="lucide lucide-alert-triangle w-5 h-5"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>
                <span className="text-xs mt-1 font-medium">Risks</span>
            </button>
            <button className="flex flex-col items-center py-2 px-1 text-gray-400 hover:text-gray-600">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="clipboard-list" className="lucide lucide-clipboard-list w-5 h-5"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"></rect><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><path d="M12 11h4"></path><path d="M12 16h4"></path><path d="M8 11h.01"></path><path d="M8 16h.01"></path></svg>
                <span className="text-xs mt-1">Plans</span>
            </button>
            <button className="flex flex-col items-center py-2 px-1 text-gray-400 hover:text-gray-600">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="menu" className="lucide lucide-menu w-5 h-5"><path d="M4 5h16"></path><path d="M4 12h16"></path><path d="M4 19h16"></path></svg>
                <span className="text-xs mt-1">More</span>
            </button>
        </div>
    </div>

    <script>
        // Initialize Lucide icons
        lucide.createIcons();
        
        // Interactive functionality
        document.addEventListener('DOMContentLoaded', function() {
            // Heatmap cell interactions
            const heatmapCells = document.querySelectorAll('.grid-cols-5 > div');
            heatmapCells.forEach(cell => {
                cell.addEventListener('click', function() {
                    // Show risk details modal (placeholder)
                    const riskCount = this.querySelector('.absolute').textContent;
                    console.log(`Clicked cell with ${riskCount} risks`);
                });
            });
            
            // Table row interactions
            const tableRows = document.querySelectorAll('tbody tr');
            tableRows.forEach(row => {
                row.addEventListener('click', function(e) {
                    if (!e.target.closest('button')) {
                        // Navigate to risk detail page
                        const riskId = this.querySelector('td').textContent;
                        console.log(`Navigate to risk ${riskId}`);
                    }
                });
            });
            
            // Filter interactions
            const filterInputs = document.querySelectorAll('input, select');
            filterInputs.forEach(input => {
                input.addEventListener('change', function() {
                    // Apply filters (placeholder)
                    console.log('Filter applied:', this.name, this.value);
                });
            });
            
            // Search functionality
            const searchInput = document.querySelector('input[placeholder*="Search"]');
            if (searchInput) {
                searchInput.addEventListener('input', function() {
                    // Implement search (placeholder)
                    console.log('Search:', this.value);
                });
            }
            
            // Sort functionality
            const sortHeaders = document.querySelectorAll('th.cursor-pointer');
            sortHeaders.forEach(header => {
                header.addEventListener('click', function() {
                    // Toggle sort direction
                    const icon = this.querySelector('i[data-lucide="chevron-up-down"]');
                    // Implement sorting logic here
                    console.log('Sort by:', this.textContent.trim());
                });
            });
            
            // AI Analysis button
            const aiButton = document.querySelector('button:has(i[data-lucide="brain"])');
            if (aiButton) {
                aiButton.addEventListener('click', function() {
                    // Show AI analysis modal
                    console.log('Show AI analysis');
                });
            }
        });
    </script>


    </div>
  );
};

export default Untitled1;