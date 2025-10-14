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
                        <a href="#" className="bg-primary-50 text-primary-700 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check-circle" className="lucide lucide-check-circle text-primary-500 mr-3 h-5 w-5"><path d="M21.801 10A10 10 0 1 1 17 3.335"></path><path d="m9 11 3 3L22 4"></path></svg>
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
                                <li className="text-gray-900 font-medium">ISO 22301 Compliance</li>
                            </ol>
                        </nav>
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900">ISO 22301 Compliance Dashboard</h1>
                                <p className="mt-1 text-sm text-gray-500">Monitor your organization's compliance with ISO 22301 Business Continuity Management standard</p>
                            </div>
                            <div className="mt-4 sm:mt-0 flex space-x-3">
                                <button className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="download" className="lucide lucide-download w-4 h-4 mr-2"><path d="M12 15V3"></path><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><path d="m7 10 5 5 5-5"></path></svg>
                                    Export Report
                                </button>
                                <button className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bot" className="lucide lucide-bot w-4 h-4 mr-2"><path d="M12 8V4H8"></path><rect width="16" height="12" x="4" y="8" rx="2"></rect><path d="M2 14h2"></path><path d="M20 14h2"></path><path d="M15 13v2"></path><path d="M9 13v2"></path></svg>
                                    AI Analysis
                                </button>
                                <button className="bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="calendar" className="lucide lucide-calendar w-4 h-4 mr-2"><path d="M8 2v4"></path><path d="M16 2v4"></path><rect width="18" height="18" x="3" y="4" rx="2"></rect><path d="M3 10h18"></path></svg>
                                    Schedule Audit
                                </button>
                            </div>
                        </div>
                    </div>

                    
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
                        
                        <div className="lg:col-span-1">
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 h-80">
                                <div className="text-center">
                                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Overall Compliance</h3>
                                    <div className="relative w-48 h-48 mx-auto mb-4">
                                        <canvas id="complianceChart" width="384" height="384" style={{display: 'block', boxSizing: 'border-box', height: '192px', width: '192px'}}></canvas>
                                        <div className="absolute inset-0 flex items-center justify-center">
                                            <div className="text-center">
                                                <div className="text-3xl font-bold text-success-600">78%</div>
                                                <div className="text-sm text-gray-500">Compliant</div>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="flex items-center justify-center space-x-4 text-sm">
                                        <div className="flex items-center">
                                            <div className="w-3 h-3 bg-success-500 rounded-full mr-2"></div>
                                            <span className="text-gray-600">Compliant (78%)</span>
                                        </div>
                                        <div className="flex items-center">
                                            <div className="w-3 h-3 bg-danger-500 rounded-full mr-2"></div>
                                            <span className="text-gray-600">Gaps (22%)</span>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        
                        <div className="lg:col-span-2">
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 h-80">
                                <h3 className="text-lg font-semibold text-gray-900 mb-4">Compliance Trend</h3>
                                <div className="h-64">
                                    <canvas id="trendChart" className="w-full h-full" width="1366" height="512" style={{display: 'block', boxSizing: 'border-box', height: '256px', width: '683px'}}></canvas>
                                </div>
                            </div>
                        </div>
                    </div>

                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Total Clauses</p>
                                    <p className="text-2xl font-bold text-gray-900">10</p>
                                </div>
                                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="list" className="lucide lucide-list w-6 h-6 text-primary-600"><path d="M3 5h.01"></path><path d="M3 12h.01"></path><path d="M3 19h.01"></path><path d="M8 5h13"></path><path d="M8 12h13"></path><path d="M8 19h13"></path></svg>
                                </div>
                            </div>
                            <div className="mt-4 flex items-center text-sm">
                                <span className="text-gray-600">ISO 22301:2019</span>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Compliant Clauses</p>
                                    <p className="text-2xl font-bold text-success-600">8</p>
                                </div>
                                <div className="w-12 h-12 bg-success-100 rounded-lg flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check-circle" className="lucide lucide-check-circle w-6 h-6 text-success-600"><path d="M21.801 10A10 10 0 1 1 17 3.335"></path><path d="m9 11 3 3L22 4"></path></svg>
                                </div>
                            </div>
                            <div className="mt-4 flex items-center text-sm">
                                <span className="text-success-600 flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="trending-up" className="lucide lucide-trending-up w-4 h-4 mr-1"><path d="M16 7h6v6"></path><path d="m22 7-8.5 8.5-5-5L2 17"></path></svg>
                                    +2 this quarter
                                </span>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Critical Gaps</p>
                                    <p className="text-2xl font-bold text-danger-600">2</p>
                                </div>
                                <div className="w-12 h-12 bg-danger-100 rounded-lg flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="alert-circle" className="lucide lucide-alert-circle w-6 h-6 text-danger-600"><circle cx="12" cy="12" r="10"></circle><line x1="12" x2="12" y1="8" y2="12"></line><line x1="12" x2="12.01" y1="16" y2="16"></line></svg>
                                </div>
                            </div>
                            <div className="mt-4 flex items-center text-sm">
                                <span className="text-danger-600 flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="alert-triangle" className="lucide lucide-alert-triangle w-4 h-4 mr-1"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>
                                    Requires attention
                                </span>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600">Evidence Items</p>
                                    <p className="text-2xl font-bold text-gray-900">156</p>
                                </div>
                                <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="file-text" className="lucide lucide-file-text w-6 h-6 text-gray-600"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"></path><path d="M14 2v4a2 2 0 0 0 2 2h4"></path><path d="M10 9H8"></path><path d="M16 13H8"></path><path d="M16 17H8"></path></svg>
                                </div>
                            </div>
                            <div className="mt-4 flex items-center text-sm">
                                <span className="text-success-600 flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="plus" className="lucide lucide-plus w-4 h-4 mr-1"><path d="M5 12h14"></path><path d="M12 5v14"></path></svg>
                                    +12 this month
                                </span>
                            </div>
                        </div>
                    </div>

                    
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
                        <div className="px-6 py-4 border-b border-gray-200">
                            <h3 className="text-lg font-semibold text-gray-900">Clause-by-Clause Analysis</h3>
                            <p className="text-sm text-gray-500 mt-1">Detailed compliance status for each ISO 22301 clause</p>
                        </div>
                        <div className="p-6">
                            <div className="space-y-4">
                                
                                <div className="border border-gray-200 rounded-lg p-4">
                                    <div className="flex items-center justify-between mb-3">
                                        <div className="flex items-center space-x-3">
                                            <div className="w-8 h-8 bg-success-100 rounded-lg flex items-center justify-center">
                                                <span className="text-sm font-bold text-success-600">4</span>
                                            </div>
                                            <div>
                                                <h4 className="font-semibold text-gray-900">Context of the organization</h4>
                                                <p className="text-sm text-gray-500">Understanding organizational context and stakeholder needs</p>
                                            </div>
                                        </div>
                                        <div className="flex items-center space-x-3">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-success-100 text-success-800">
                                                Compliant
                                            </span>
                                            <span className="text-sm font-medium text-success-600">95%</span>
                                        </div>
                                    </div>
                                    <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                                        <div className="bg-success-500 h-2 rounded-full" style={{width: '95%'}}></div>
                                    </div>
                                    <div className="flex items-center justify-between text-sm text-gray-600">
                                        <span>Evidence: 18 items</span>
                                        <span>Last updated: 1 week ago</span>
                                    </div>
                                </div>

                                
                                <div className="border border-gray-200 rounded-lg p-4">
                                    <div className="flex items-center justify-between mb-3">
                                        <div className="flex items-center space-x-3">
                                            <div className="w-8 h-8 bg-success-100 rounded-lg flex items-center justify-center">
                                                <span className="text-sm font-bold text-success-600">5</span>
                                            </div>
                                            <div>
                                                <h4 className="font-semibold text-gray-900">Leadership</h4>
                                                <p className="text-sm text-gray-500">Leadership commitment and policy establishment</p>
                                            </div>
                                        </div>
                                        <div className="flex items-center space-x-3">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-success-100 text-success-800">
                                                Compliant
                                            </span>
                                            <span className="text-sm font-medium text-success-600">88%</span>
                                        </div>
                                    </div>
                                    <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                                        <div className="bg-success-500 h-2 rounded-full" style={{width: '88%'}}></div>
                                    </div>
                                    <div className="flex items-center justify-between text-sm text-gray-600">
                                        <span>Evidence: 14 items</span>
                                        <span>Last updated: 3 days ago</span>
                                    </div>
                                </div>

                                
                                <div className="border border-gray-200 rounded-lg p-4">
                                    <div className="flex items-center justify-between mb-3">
                                        <div className="flex items-center space-x-3">
                                            <div className="w-8 h-8 bg-warning-100 rounded-lg flex items-center justify-center">
                                                <span className="text-sm font-bold text-warning-600">6</span>
                                            </div>
                                            <div>
                                                <h4 className="font-semibold text-gray-900">Planning</h4>
                                                <p className="text-sm text-gray-500">Risk assessment and business continuity objectives</p>
                                            </div>
                                        </div>
                                        <div className="flex items-center space-x-3">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-warning-100 text-warning-800">
                                                Partial
                                            </span>
                                            <span className="text-sm font-medium text-warning-600">72%</span>
                                        </div>
                                    </div>
                                    <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                                        <div className="bg-warning-500 h-2 rounded-full" style={{width: '72%'}}></div>
                                    </div>
                                    <div className="flex items-center justify-between text-sm text-gray-600">
                                        <span>Evidence: 12 items</span>
                                        <span>Gap: Risk assessment documentation</span>
                                    </div>
                                </div>

                                
                                <div className="border border-gray-200 rounded-lg p-4">
                                    <div className="flex items-center justify-between mb-3">
                                        <div className="flex items-center space-x-3">
                                            <div className="w-8 h-8 bg-success-100 rounded-lg flex items-center justify-center">
                                                <span className="text-sm font-bold text-success-600">7</span>
                                            </div>
                                            <div>
                                                <h4 className="font-semibold text-gray-900">Support</h4>
                                                <p className="text-sm text-gray-500">Resources, competence, and communication</p>
                                            </div>
                                        </div>
                                        <div className="flex items-center space-x-3">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-success-100 text-success-800">
                                                Compliant
                                            </span>
                                            <span className="text-sm font-medium text-success-600">85%</span>
                                        </div>
                                    </div>
                                    <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                                        <div className="bg-success-500 h-2 rounded-full" style={{width: '85%'}}></div>
                                    </div>
                                    <div className="flex items-center justify-between text-sm text-gray-600">
                                        <span>Evidence: 22 items</span>
                                        <span>Last updated: 5 days ago</span>
                                    </div>
                                </div>

                                
                                <div className="border border-gray-200 rounded-lg p-4">
                                    <div className="flex items-center justify-between mb-3">
                                        <div className="flex items-center space-x-3">
                                            <div className="w-8 h-8 bg-danger-100 rounded-lg flex items-center justify-center">
                                                <span className="text-sm font-bold text-danger-600">8</span>
                                            </div>
                                            <div>
                                                <h4 className="font-semibold text-gray-900">Operation</h4>
                                                <p className="text-sm text-gray-500">Business impact analysis and continuity strategies</p>
                                            </div>
                                        </div>
                                        <div className="flex items-center space-x-3">
                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-danger-100 text-danger-800">
                                                Non-Compliant
                                            </span>
                                            <span className="text-sm font-medium text-danger-600">45%</span>
                                        </div>
                                    </div>
                                    <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
                                        <div className="bg-danger-500 h-2 rounded-full" style={{width: '45%'}}></div>
                                    </div>
                                    <div className="flex items-center justify-between text-sm text-gray-600">
                                        <span>Evidence: 8 items</span>
                                        <span className="text-danger-600">Critical gap: BIA incomplete</span>
                                    </div>
                                </div>

                                
                                <button className="w-full py-3 text-sm text-primary-600 hover:text-primary-700 font-medium border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors">
                                    Show All Clauses (10)
                                </button>
                            </div>
                        </div>
                    </div>

                    
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                        
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                            <div className="px-6 py-4 border-b border-gray-200">
                                <h3 className="text-lg font-semibold text-gray-900">Gap Analysis</h3>
                                <p className="text-sm text-gray-500 mt-1">Critical gaps requiring immediate attention</p>
                            </div>
                            <div className="p-6">
                                <div className="space-y-4">
                                    <div className="border-l-4 border-danger-500 bg-danger-50 p-4 rounded-r-lg">
                                        <div className="flex items-start justify-between">
                                            <div>
                                                <h4 className="font-semibold text-danger-900">Business Impact Analysis Incomplete</h4>
                                                <p className="text-sm text-danger-700 mt-1">Clause 8.2 - Critical business processes not fully analyzed</p>
                                                <p className="text-xs text-danger-600 mt-2">Priority: Critical | Due: 2 weeks</p>
                                            </div>
                                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-danger-100 text-danger-800">
                                                Critical
                                            </span>
                                        </div>
                                    </div>

                                    <div className="border-l-4 border-warning-500 bg-warning-50 p-4 rounded-r-lg">
                                        <div className="flex items-start justify-between">
                                            <div>
                                                <h4 className="font-semibold text-warning-900">Risk Assessment Documentation</h4>
                                                <p className="text-sm text-warning-700 mt-1">Clause 6.1 - Risk register needs updating with new threats</p>
                                                <p className="text-xs text-warning-600 mt-2">Priority: High | Due: 1 month</p>
                                            </div>
                                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-warning-100 text-warning-800">
                                                High
                                            </span>
                                        </div>
                                    </div>

                                    <div className="border-l-4 border-yellow-500 bg-yellow-50 p-4 rounded-r-lg">
                                        <div className="flex items-start justify-between">
                                            <div>
                                                <h4 className="font-semibold text-yellow-900">Training Records</h4>
                                                <p className="text-sm text-yellow-700 mt-1">Clause 7.2 - Staff competency records need updating</p>
                                                <p className="text-xs text-yellow-600 mt-2">Priority: Medium | Due: 6 weeks</p>
                                            </div>
                                            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                                                Medium
                                            </span>
                                        </div>
                                    </div>
                                </div>

                                <div className="mt-6">
                                    <button className="w-full bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors">
                                        Create Action Plan
                                    </button>
                                </div>
                            </div>
                        </div>

                        
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                            <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
                                <div>
                                    <h3 className="text-lg font-semibold text-gray-900">Evidence Library</h3>
                                    <p className="text-sm text-gray-500 mt-1">Supporting documentation and evidence</p>
                                </div>
                                <button className="bg-primary-600 text-white px-3 py-1.5 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="upload" className="lucide lucide-upload w-4 h-4 mr-2"><path d="M12 3v12"></path><path d="m17 8-5-5-5 5"></path><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path></svg>
                                    Upload
                                </button>
                            </div>
                            <div className="p-6">
                                <div className="space-y-3">
                                    <div className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50">
                                        <div className="flex items-center space-x-3">
                                            <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="file-text" className="lucide lucide-file-text w-4 h-4 text-blue-600"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"></path><path d="M14 2v4a2 2 0 0 0 2 2h4"></path><path d="M10 9H8"></path><path d="M16 13H8"></path><path d="M16 17H8"></path></svg>
                                            </div>
                                            <div>
                                                <p className="text-sm font-medium text-gray-900">BC Policy Document</p>
                                                <p className="text-xs text-gray-500">Clause 5.2 | Updated 2 days ago</p>
                                            </div>
                                        </div>
                                        <button className="text-gray-400 hover:text-gray-600">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="download" className="lucide lucide-download w-4 h-4"><path d="M12 15V3"></path><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><path d="m7 10 5 5 5-5"></path></svg>
                                        </button>
                                    </div>

                                    <div className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50">
                                        <div className="flex items-center space-x-3">
                                            <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="file-spreadsheet" className="lucide lucide-file-spreadsheet w-4 h-4 text-green-600"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"></path><path d="M14 2v4a2 2 0 0 0 2 2h4"></path><path d="M8 13h2"></path><path d="M14 13h2"></path><path d="M8 17h2"></path><path d="M14 17h2"></path></svg>
                                            </div>
                                            <div>
                                                <p className="text-sm font-medium text-gray-900">Risk Register</p>
                                                <p className="text-xs text-gray-500">Clause 6.1 | Updated 1 week ago</p>
                                            </div>
                                        </div>
                                        <button className="text-gray-400 hover:text-gray-600">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="download" className="lucide lucide-download w-4 h-4"><path d="M12 15V3"></path><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><path d="m7 10 5 5 5-5"></path></svg>
                                        </button>
                                    </div>

                                    <div className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50">
                                        <div className="flex items-center space-x-3">
                                            <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="video" className="lucide lucide-video w-4 h-4 text-purple-600"><path d="m16 13 5.223 3.482a.5.5 0 0 0 .777-.416V7.87a.5.5 0 0 0-.752-.432L16 10.5"></path><rect x="2" y="6" width="14" height="12" rx="2"></rect></svg>
                                            </div>
                                            <div>
                                                <p className="text-sm font-medium text-gray-900">Training Video</p>
                                                <p className="text-xs text-gray-500">Clause 7.2 | Added 3 days ago</p>
                                            </div>
                                        </div>
                                        <button className="text-gray-400 hover:text-gray-600">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="play" className="lucide lucide-play w-4 h-4"><path d="M5 5a2 2 0 0 1 3.008-1.728l11.997 6.998a2 2 0 0 1 .003 3.458l-12 7A2 2 0 0 1 5 19z"></path></svg>
                                        </button>
                                    </div>

                                    <div className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50">
                                        <div className="flex items-center space-x-3">
                                            <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="image" className="lucide lucide-image w-4 h-4 text-orange-600"><rect width="18" height="18" x="3" y="3" rx="2" ry="2"></rect><circle cx="9" cy="9" r="2"></circle><path d="m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21"></path></svg>
                                            </div>
                                            <div>
                                                <p className="text-sm font-medium text-gray-900">Exercise Photos</p>
                                                <p className="text-xs text-gray-500">Clause 9.1 | Added 1 week ago</p>
                                            </div>
                                        </div>
                                        <button className="text-gray-400 hover:text-gray-600">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="eye" className="lucide lucide-eye w-4 h-4"><path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"></path><circle cx="12" cy="12" r="3"></circle></svg>
                                        </button>
                                    </div>

                                    <div className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50">
                                        <div className="flex items-center space-x-3">
                                            <div className="w-8 h-8 bg-red-100 rounded-lg flex items-center justify-center">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="file-check" className="lucide lucide-file-check w-4 h-4 text-red-600"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"></path><path d="M14 2v4a2 2 0 0 0 2 2h4"></path><path d="m9 15 2 2 4-4"></path></svg>
                                            </div>
                                            <div>
                                                <p className="text-sm font-medium text-gray-900">Audit Report</p>
                                                <p className="text-xs text-gray-500">Clause 9.2 | Added 2 weeks ago</p>
                                            </div>
                                        </div>
                                        <button className="text-gray-400 hover:text-gray-600">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="download" className="lucide lucide-download w-4 h-4"><path d="M12 15V3"></path><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><path d="m7 10 5 5 5-5"></path></svg>
                                        </button>
                                    </div>
                                </div>

                                <div className="mt-4 text-center">
                                    <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
                                        View All Evidence (156 items)
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
            <button className="flex flex-col items-center py-2 px-1 text-gray-400 hover:text-gray-600">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="alert-triangle" className="lucide lucide-alert-triangle w-5 h-5"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>
                <span className="text-xs mt-1">Risks</span>
            </button>
            <button className="flex flex-col items-center py-2 px-1 text-gray-400 hover:text-gray-600">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="clipboard-list" className="lucide lucide-clipboard-list w-5 h-5"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"></rect><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><path d="M12 11h4"></path><path d="M12 16h4"></path><path d="M8 11h.01"></path><path d="M8 16h.01"></path></svg>
                <span className="text-xs mt-1">Plans</span>
            </button>
            <button className="flex flex-col items-center py-2 px-1 text-primary-600 bg-primary-50 rounded-lg">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check-circle" className="lucide lucide-check-circle w-5 h-5"><path d="M21.801 10A10 10 0 1 1 17 3.335"></path><path d="m9 11 3 3L22 4"></path></svg>
                <span className="text-xs mt-1 font-medium">Compliance</span>
            </button>
        </div>
    </div>

    <script>
        // Initialize Lucide icons
        lucide.createIcons();
        
        // Initialize Charts
        document.addEventListener('DOMContentLoaded', function() {
            // Compliance Donut Chart
            const complianceCtx = document.getElementById('complianceChart').getContext('2d');
            new Chart(complianceCtx, {
                type: 'doughnut',
                data: {
                    datasets: [{
                        data: [78, 22],
                        backgroundColor: ['#22c55e', '#ef4444'],
                        borderWidth: 0
                    }]
                },
                options: {
                    responsive: false,
                    maintainAspectRatio: false,
                    cutout: '70%',
                    plugins: {
                        legend: {
                            display: false
                        },
                        tooltip: {
                            enabled: false
                        }
                    }
                }
            });
            
            // Compliance Trend Chart
            const trendCtx = document.getElementById('trendChart').getContext('2d');
            new Chart(trendCtx, {
                type: 'line',
                data: {
                    labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'],
                    datasets: [{
                        label: 'Compliance Score',
                        data: [45, 52, 58, 65, 68, 72, 75, 76, 77, 78],
                        borderColor: '#3b82f6',
                        backgroundColor: 'rgba(59, 130, 246, 0.1)',
                        fill: true,
                        tension: 0.4
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
                            max: 100,
                            ticks: {
                                callback: function(value) {
                                    return value + '%';
                                }
                            }
                        }
                    }
                }
            });
            
            // Interactive functionality
            const exportBtn = document.querySelector('button:has(i[data-lucide="download"])');
            if (exportBtn) {
                exportBtn.addEventListener('click', function() {
                    console.log('Export compliance report');
                });
            }
            
            const aiAnalysisBtn = document.querySelector('button:has(i[data-lucide="bot"])');
            if (aiAnalysisBtn) {
                aiAnalysisBtn.addEventListener('click', function() {
                    console.log('AI compliance analysis');
                });
            }
            
            const scheduleAuditBtn = document.querySelector('button:has(i[data-lucide="calendar"])');
            if (scheduleAuditBtn) {
                scheduleAuditBtn.addEventListener('click', function() {
                    console.log('Schedule audit');
                });
            }
            
            // Evidence library interactions
            const evidenceItems = document.querySelectorAll('.evidence-item');
            evidenceItems.forEach(item => {
                item.addEventListener('click', function() {
                    const fileName = this.querySelector('p').textContent;
                    console.log('View evidence:', fileName);
                });
            });
            
            // Upload evidence
            const uploadBtn = document.querySelector('button:has(i[data-lucide="upload"])');
            if (uploadBtn) {
                uploadBtn.addEventListener('click', function() {
                    console.log('Upload evidence');
                });
            }
            
            // Create action plan
            const actionPlanBtn = document.querySelector('button:contains("Create Action Plan")');
            if (actionPlanBtn) {
                actionPlanBtn.addEventListener('click', function() {
                    console.log('Create action plan for gaps');
                });
            }
        });
    </script>


    </div>
  );
};

export default Untitled1;