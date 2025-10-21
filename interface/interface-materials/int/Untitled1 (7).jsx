import React from 'react';

const Untitled1 = () => {
  return (
    <div>
      
    
    <nav className="bg-white border-b border-gray-200 px-4 py-3 sm:px-6">
        <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center" style={{transition: 'width 1s ease-in-out'}}>
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="shield-check" className="lucide lucide-shield-check w-6 h-6 text-white"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"></path><path d="m9 12 2 2 4-4"></path></svg>
                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-gray-900">AI-Platform-ISO</h1>
                        <p className="text-xs text-gray-500">Business Continuity Management</p>
                    </div>
                </div>
            </div>
            <div className="flex items-center space-x-3">
                <div className="relative">
                    <input type="text" placeholder="Search..." className="w-64 pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm" />
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="search" className="lucide lucide-search w-4 h-4 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2"><path d="m21 21-4.34-4.34"></path><circle cx="11" cy="11" r="8"></circle></svg>
                </div>
                <button className="relative p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bell" className="lucide lucide-bell w-5 h-5"><path d="M10.268 21a2 2 0 0 0 3.464 0"></path><path d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326"></path></svg>
                    <div className="absolute -top-1 -right-1 w-3 h-3 bg-danger-500 rounded-full"></div>
                </button>
                <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bot" className="lucide lucide-bot w-5 h-5"><path d="M12 8V4H8"></path><rect width="16" height="12" x="4" y="8" rx="2"></rect><path d="M2 14h2"></path><path d="M20 14h2"></path><path d="M15 13v2"></path><path d="M9 13v2"></path></svg>
                </button>
                <div className="flex items-center space-x-3 pl-3 border-l border-gray-200">
                    <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                        <span className="text-sm font-medium text-primary-600">JD</span>
                    </div>
                    <div className="hidden md:block">
                        <p className="text-sm font-medium text-gray-900">John Doe</p>
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
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="layout-dashboard" className="lucide lucide-layout-dashboard text-gray-400 mr-3 h-5 w-5"><rect width="7" height="9" x="3" y="3" rx="1"></rect><rect width="7" height="5" x="14" y="3" rx="1"></rect><rect width="7" height="9" x="14" y="12" rx="1"></rect><rect width="7" height="5" x="3" y="16" rx="1"></rect></svg>
                            Dashboard
                        </a>
                        <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="target" className="lucide lucide-target text-gray-400 mr-3 h-5 w-5"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>
                            BCM Journey
                        </a>
                        <a href="#" className="bg-primary-50 text-primary-700 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bar-chart-3" className="lucide lucide-bar-chart-3 text-primary-500 mr-3 h-5 w-5"><path d="M3 3v16a2 2 0 0 0 2 2h16"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>
                            BIA
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
                            Exercises
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
                        <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="graduation-cap" className="lucide lucide-graduation-cap text-gray-400 mr-3 h-5 w-5"><path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z"></path><path d="M22 10v6"></path><path d="M6 12.5V16a6 3 0 0 0 12 0v-3.5"></path></svg>
                            Learning
                        </a>
                        <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="user" className="lucide lucide-user text-gray-400 mr-3 h-5 w-5"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                            Profile
                        </a>
                    </nav>
                </div>
            </div>
        </aside>

        
        <main className="flex-1 overflow-y-auto">
            <div className="py-6">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    
                    <nav className="flex mb-6" aria-label="Breadcrumb">
                        <ol className="flex items-center space-x-2">
                            <li>
                                <a href="#" className="text-gray-400 hover:text-gray-600 text-sm">BIA</a>
                            </li>
                            <li>
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="chevron-right" className="lucide lucide-chevron-right w-4 h-4 text-gray-400"><path d="m9 18 6-6-6-6"></path></svg>
                            </li>
                            <li>
                                <span className="text-gray-900 text-sm font-medium">Financial Services BIA 2024</span>
                            </li>
                        </ol>
                    </nav>

                    
                    <div className="mb-8">
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                            <div className="flex items-center space-x-4">
                                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bar-chart-3" className="lucide lucide-bar-chart-3 w-6 h-6 text-primary-600"><path d="M3 3v16a2 2 0 0 0 2 2h16"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>
                                </div>
                                <div>
                                    <h1 className="text-2xl font-bold text-gray-900">Financial Services BIA 2024</h1>
                                    <div className="flex items-center space-x-4 mt-1">
                                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-success-100 text-success-800">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check-circle" className="lucide lucide-check-circle w-3 h-3 mr-1"><path d="M21.801 10A10 10 0 1 1 17 3.335"></path><path d="m9 11 3 3L22 4"></path></svg>
                                            Completed
                                        </span>
                                        <span className="text-sm text-gray-500">Last updated: Dec 8, 2024</span>
                                        <span className="text-sm text-gray-500">Owner: Sarah Johnson</span>
                                    </div>
                                </div>
                            </div>
                            <div className="mt-4 sm:mt-0 flex space-x-3">
                                <button className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="download" className="lucide lucide-download w-4 h-4 mr-2"><path d="M12 15V3"></path><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><path d="m7 10 5 5 5-5"></path></svg>
                                    Export Report
                                </button>
                                <button className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="share" className="lucide lucide-share w-4 h-4 mr-2"><path d="M12 2v13"></path><path d="m16 6-4-4-4 4"></path><path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path></svg>
                                    Share
                                </button>
                                <button className="bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors flex items-center" style={{transition: 'width 1s ease-in-out'}}>
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="edit" className="lucide lucide-edit w-4 h-4 mr-2"><path d="M12 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.375 2.625a1 1 0 0 1 3 3l-9.013 9.014a2 2 0 0 1-.853.505l-2.873.84a.5.5 0 0 1-.62-.62l.84-2.873a2 2 0 0 1 .506-.852z"></path></svg>
                                    Edit BIA
                                </button>
                            </div>
                        </div>
                    </div>

                    
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-8">
                        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                            <div className="text-center">
                                <div className="text-2xl font-bold text-gray-900">100%</div>
                                <div className="text-sm text-gray-500">Completion</div>
                            </div>
                            <div className="text-center">
                                <div className="text-2xl font-bold text-primary-600">24</div>
                                <div className="text-sm text-gray-500">Processes Analyzed</div>
                            </div>
                            <div className="text-center">
                                <div className="text-2xl font-bold text-warning-600">8</div>
                                <div className="text-sm text-gray-500">Critical Processes</div>
                            </div>
                            <div className="text-center">
                                <div className="text-2xl font-bold text-success-600">4.2</div>
                                <div className="text-sm text-gray-500">AI Quality Score</div>
                            </div>
                        </div>
                    </div>

                    
                    <div className="bg-white rounded-lg shadow-sm border border-gray-200 mb-8">
                        <div className="border-b border-gray-200">
                            <nav className="-mb-px flex space-x-8 px-6" aria-label="Tabs">
                                <button className="border-primary-500 text-primary-600 whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm" data-tab="overview">
                                    Overview
                                </button>
                                <button className="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm" data-tab="processes">
                                    Processes (24)
                                </button>
                                <button className="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm" data-tab="dependencies">
                                    Dependencies
                                </button>
                                <button className="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm" data-tab="impact">
                                    Impact Analysis
                                </button>
                                <button className="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm" data-tab="report">
                                    Report
                                </button>
                                <button className="border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm" data-tab="history">
                                    History
                                </button>
                            </nav>
                        </div>

                        
                        <div className="p-6">
                            
                            <div id="overview-tab" className="tab-content">
                                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                                    
                                    <div className="space-y-6">
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-900 mb-4">BIA Summary</h3>
                                            <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                                                <div className="flex justify-between">
                                                    <span className="text-sm text-gray-600">Scope:</span>
                                                    <span className="text-sm font-medium text-gray-900">Core Financial Services</span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span className="text-sm text-gray-600">Duration:</span>
                                                    <span className="text-sm font-medium text-gray-900">6 weeks</span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span className="text-sm text-gray-600">Methodology:</span>
                                                    <span className="text-sm font-medium text-gray-900">ISO 22301 + AI-Enhanced</span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span className="text-sm text-gray-600">Participants:</span>
                                                    <span className="text-sm font-medium text-gray-900">12 stakeholders</span>
                                                </div>
                                                <div className="flex justify-between">
                                                    <span className="text-sm text-gray-600">Status:</span>
                                                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-success-100 text-success-800">
                                                        Completed
                                                    </span>
                                                </div>
                                            </div>
                                        </div>

                                        
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Findings</h3>
                                            <div className="space-y-3">
                                                <div className="flex items-start space-x-3 p-3 bg-red-50 rounded-lg">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="alert-circle" className="lucide lucide-alert-circle w-5 h-5 text-red-600 mt-0.5"><circle cx="12" cy="12" r="10"></circle><line x1="12" x2="12" y1="8" y2="12"></line><line x1="12" x2="12.01" y1="16" y2="16"></line></svg>
                                                    <div>
                                                        <p className="text-sm font-medium text-red-900">Critical Dependency Risk</p>
                                                        <p className="text-sm text-red-700">Payment processing system has single point of failure</p>
                                                    </div>
                                                </div>
                                                <div className="flex items-start space-x-3 p-3 bg-yellow-50 rounded-lg">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="alert-triangle" className="lucide lucide-alert-triangle w-5 h-5 text-yellow-600 mt-0.5"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>
                                                    <div>
                                                        <p className="text-sm font-medium text-yellow-900">RTO Gap Identified</p>
                                                        <p className="text-sm text-yellow-700">Customer service RTO exceeds business requirements</p>
                                                    </div>
                                                </div>
                                                <div className="flex items-start space-x-3 p-3 bg-green-50 rounded-lg">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check-circle" className="lucide lucide-check-circle w-5 h-5 text-green-600 mt-0.5"><path d="M21.801 10A10 10 0 1 1 17 3.335"></path><path d="m9 11 3 3L22 4"></path></svg>
                                                    <div>
                                                        <p className="text-sm font-medium text-green-900">Strong Backup Systems</p>
                                                        <p className="text-sm text-green-700">Data backup and recovery processes exceed requirements</p>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Insights</h3>
                                            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                                                <div className="flex items-start space-x-3">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bot" className="lucide lucide-bot w-5 h-5 text-blue-600 mt-0.5"><path d="M12 8V4H8"></path><rect width="16" height="12" x="4" y="8" rx="2"></rect><path d="M2 14h2"></path><path d="M20 14h2"></path><path d="M15 13v2"></path><path d="M9 13v2"></path></svg>
                                                    <div>
                                                        <p className="text-sm font-medium text-blue-900 mb-2">AI Recommendations</p>
                                                        <ul className="text-sm text-blue-800 space-y-1">
                                                            <li>• Implement redundant payment processing infrastructure</li>
                                                            <li>• Reduce customer service RTO from 4h to 2h</li>
                                                            <li>• Consider cloud-based backup for critical systems</li>
                                                            <li>• Establish vendor SLA monitoring for key dependencies</li>
                                                        </ul>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    
                                    <div className="space-y-6">
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-900 mb-4">Process Criticality Distribution</h3>
                                            <div className="bg-gray-50 rounded-lg p-6 h-80">
                                                <div className="flex items-center justify-center h-full">
                                                    <div className="text-center">
                                                        <div className="grid grid-cols-2 gap-4 mb-6">
                                                            <div className="text-center">
                                                                <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-2">
                                                                    <span className="text-xl font-bold text-red-600">8</span>
                                                                </div>
                                                                <p className="text-sm font-medium text-gray-900">Critical</p>
                                                                <p className="text-xs text-gray-500">33%</p>
                                                            </div>
                                                            <div className="text-center">
                                                                <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-2">
                                                                    <span className="text-xl font-bold text-yellow-600">10</span>
                                                                </div>
                                                                <p className="text-sm font-medium text-gray-900">High</p>
                                                                <p className="text-xs text-gray-500">42%</p>
                                                            </div>
                                                            <div className="text-center">
                                                                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
                                                                    <span className="text-xl font-bold text-blue-600">4</span>
                                                                </div>
                                                                <p className="text-sm font-medium text-gray-900">Medium</p>
                                                                <p className="text-xs text-gray-500">17%</p>
                                                            </div>
                                                            <div className="text-center">
                                                                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
                                                                    <span className="text-xl font-bold text-green-600">2</span>
                                                                </div>
                                                                <p className="text-sm font-medium text-gray-900">Low</p>
                                                                <p className="text-xs text-gray-500">8%</p>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-900 mb-4">RTO/RPO Summary</h3>
                                            <div className="space-y-4">
                                                <div className="bg-gray-50 rounded-lg p-4">
                                                    <div className="flex items-center justify-between mb-2">
                                                        <span className="text-sm font-medium text-gray-900">Average RTO</span>
                                                        <span className="text-sm font-bold text-primary-600">2.5 hours</span>
                                                    </div>
                                                    <div className="w-full bg-gray-200 rounded-full h-2">
                                                        <div className="bg-primary-600 h-2 rounded-full" style={{width: '65%', transition: 'width 1s ease-in-out'}}></div>
                                                    </div>
                                                    <p className="text-xs text-gray-500 mt-1">Target: 4 hours</p>
                                                </div>
                                                
                                                <div className="bg-gray-50 rounded-lg p-4">
                                                    <div className="flex items-center justify-between mb-2">
                                                        <span className="text-sm font-medium text-gray-900">Average RPO</span>
                                                        <span className="text-sm font-bold text-success-600">15 minutes</span>
                                                    </div>
                                                    <div className="w-full bg-gray-200 rounded-full h-2">
                                                        <div className="bg-success-600 h-2 rounded-full" style={{width: '85%', transition: 'width 1s ease-in-out'}}></div>
                                                    </div>
                                                    <p className="text-xs text-gray-500 mt-1">Target: 1 hour</p>
                                                </div>
                                            </div>
                                        </div>

                                        
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-900 mb-4">Recommended Next Steps</h3>
                                            <div className="space-y-3">
                                                <div className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg">
                                                    <div className="w-6 h-6 bg-primary-100 rounded-full flex items-center justify-center">
                                                        <span className="text-xs font-bold text-primary-600">1</span>
                                                    </div>
                                                    <span className="text-sm text-gray-900">Create BC Plans for critical processes</span>
                                                </div>
                                                <div className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg">
                                                    <div className="w-6 h-6 bg-primary-100 rounded-full flex items-center justify-center">
                                                        <span className="text-xs font-bold text-primary-600">2</span>
                                                    </div>
                                                    <span className="text-sm text-gray-900">Conduct risk assessment for identified dependencies</span>
                                                </div>
                                                <div className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg">
                                                    <div className="w-6 h-6 bg-primary-100 rounded-full flex items-center justify-center">
                                                        <span className="text-xs font-bold text-primary-600">3</span>
                                                    </div>
                                                    <span className="text-sm text-gray-900">Schedule tabletop exercise for payment processing</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            
                            <div id="processes-tab" className="tab-content hidden">
                                <div className="space-y-6">
                                    
                                    <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between space-y-3 sm:space-y-0">
                                        <div className="flex space-x-3">
                                            <select className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                                                <option>All Criticality Levels</option>
                                                <option>Critical</option>
                                                <option>High</option>
                                                <option>Medium</option>
                                                <option>Low</option>
                                            </select>
                                            <select className="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                                                <option>All Departments</option>
                                                <option>Operations</option>
                                                <option>Customer Service</option>
                                                <option>IT</option>
                                                <option>Finance</option>
                                            </select>
                                        </div>
                                        <div className="relative">
                                            <input type="text" placeholder="Search processes..." className="w-64 pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm" />
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="search" className="lucide lucide-search w-4 h-4 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2"><path d="m21 21-4.34-4.34"></path><circle cx="11" cy="11" r="8"></circle></svg>
                                        </div>
                                    </div>

                                    
                                    <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
                                        <div className="overflow-x-auto">
                                            <table className="min-w-full divide-y divide-gray-200">
                                                <thead className="bg-gray-50">
                                                    <tr>
                                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Process</th>
                                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Department</th>
                                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Criticality</th>
                                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">RTO</th>
                                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">RPO</th>
                                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Dependencies</th>
                                                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                                                    </tr>
                                                </thead>
                                                <tbody className="bg-white divide-y divide-gray-200">
                                                    <tr className="hover:bg-gray-50">
                                                        <td className="px-6 py-4 whitespace-nowrap">
                                                            <div className="text-sm font-medium text-gray-900">Payment Processing</div>
                                                            <div className="text-sm text-gray-500">Core transaction processing system</div>
                                                        </td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">Operations</td>
                                                        <td className="px-6 py-4 whitespace-nowrap">
                                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                                                Critical
                                                            </span>
                                                        </td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">1 hour</td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">5 minutes</td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">3</td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                                            <button className="text-primary-600 hover:text-primary-900">View Details</button>
                                                        </td>
                                                    </tr>
                                                    <tr className="hover:bg-gray-50">
                                                        <td className="px-6 py-4 whitespace-nowrap">
                                                            <div className="text-sm font-medium text-gray-900">Customer Authentication</div>
                                                            <div className="text-sm text-gray-500">User login and verification system</div>
                                                        </td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">IT</td>
                                                        <td className="px-6 py-4 whitespace-nowrap">
                                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
                                                                Critical
                                                            </span>
                                                        </td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">30 minutes</td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">10 minutes</td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">2</td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                                            <button className="text-primary-600 hover:text-primary-900">View Details</button>
                                                        </td>
                                                    </tr>
                                                    <tr className="hover:bg-gray-50">
                                                        <td className="px-6 py-4 whitespace-nowrap">
                                                            <div className="text-sm font-medium text-gray-900">Customer Service Portal</div>
                                                            <div className="text-sm text-gray-500">Online customer support system</div>
                                                        </td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">Customer Service</td>
                                                        <td className="px-6 py-4 whitespace-nowrap">
                                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                                                                High
                                                            </span>
                                                        </td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">4 hours</td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">1 hour</td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">4</td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                                            <button className="text-primary-600 hover:text-primary-900">View Details</button>
                                                        </td>
                                                    </tr>
                                                    <tr className="hover:bg-gray-50">
                                                        <td className="px-6 py-4 whitespace-nowrap">
                                                            <div className="text-sm font-medium text-gray-900">Account Management</div>
                                                            <div className="text-sm text-gray-500">Customer account operations</div>
                                                        </td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">Operations</td>
                                                        <td className="px-6 py-4 whitespace-nowrap">
                                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                                                                High
                                                            </span>
                                                        </td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">2 hours</td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">30 minutes</td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">5</td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                                            <button className="text-primary-600 hover:text-primary-900">View Details</button>
                                                        </td>
                                                    </tr>
                                                    <tr className="hover:bg-gray-50">
                                                        <td className="px-6 py-4 whitespace-nowrap">
                                                            <div className="text-sm font-medium text-gray-900">Reporting System</div>
                                                            <div className="text-sm text-gray-500">Financial and operational reporting</div>
                                                        </td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">Finance</td>
                                                        <td className="px-6 py-4 whitespace-nowrap">
                                                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                                                Medium
                                                            </span>
                                                        </td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">8 hours</td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">4 hours</td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">2</td>
                                                        <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                                                            <button className="text-primary-600 hover:text-primary-900">View Details</button>
                                                        </td>
                                                    </tr>
                                                </tbody>
                                            </table>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            
                            <div id="dependencies-tab" className="tab-content hidden">
                                <div className="text-center py-12">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="network" className="lucide lucide-network w-12 h-12 text-gray-400 mx-auto mb-4"><rect x="16" y="16" width="6" height="6" rx="1"></rect><rect x="2" y="16" width="6" height="6" rx="1"></rect><rect x="9" y="2" width="6" height="6" rx="1"></rect><path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3"></path><path d="M12 12V8"></path></svg>
                                    <h3 className="text-lg font-medium text-gray-900 mb-2">Dependency Mapping</h3>
                                    <p className="text-gray-500">Interactive dependency visualization would be displayed here</p>
                                </div>
                            </div>

                            <div id="impact-tab" className="tab-content hidden">
                                <div className="text-center py-12">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="trending-down" className="lucide lucide-trending-down w-12 h-12 text-gray-400 mx-auto mb-4"><path d="M16 17h6v-6"></path><path d="m22 17-8.5-8.5-5 5L2 7"></path></svg>
                                    <h3 className="text-lg font-medium text-gray-900 mb-2">Impact Analysis</h3>
                                    <p className="text-gray-500">Detailed impact analysis charts and metrics would be displayed here</p>
                                </div>
                            </div>

                            <div id="report-tab" className="tab-content hidden">
                                <div className="text-center py-12">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="file-text" className="lucide lucide-file-text w-12 h-12 text-gray-400 mx-auto mb-4"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"></path><path d="M14 2v4a2 2 0 0 0 2 2h4"></path><path d="M10 9H8"></path><path d="M16 13H8"></path><path d="M16 17H8"></path></svg>
                                    <h3 className="text-lg font-medium text-gray-900 mb-2">BIA Report</h3>
                                    <p className="text-gray-500">Generated BIA report preview and download options would be displayed here</p>
                                </div>
                            </div>

                            <div id="history-tab" className="tab-content hidden">
                                <div className="text-center py-12">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="clock" className="lucide lucide-clock w-12 h-12 text-gray-400 mx-auto mb-4"><path d="M12 6v6l4 2"></path><circle cx="12" cy="12" r="10"></circle></svg>
                                    <h3 className="text-lg font-medium text-gray-900 mb-2">Change History</h3>
                                    <p className="text-gray-500">Audit trail and change history would be displayed here</p>
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
            <button className="flex flex-col items-center py-2 px-1 text-primary-600 bg-primary-50 rounded-lg">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bar-chart-3" className="lucide lucide-bar-chart-3 w-5 h-5"><path d="M3 3v16a2 2 0 0 0 2 2h16"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>
                <span className="text-xs mt-1 font-medium">BIA</span>
            </button>
            <button className="flex flex-col items-center py-2 px-1 text-gray-400 hover:text-gray-600">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="alert-triangle" className="lucide lucide-alert-triangle w-5 h-5"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>
                <span className="text-xs mt-1">Risks</span>
            </button>
            <button className="flex flex-col items-center py-2 px-1 text-gray-400 hover:text-gray-600">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="clipboard-list" className="lucide lucide-clipboard-list w-5 h-5"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"></rect><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><path d="M12 11h4"></path><path d="M12 16h4"></path><path d="M8 11h.01"></path><path d="M8 16h.01"></path></svg>
                <span className="text-xs mt-1">Plans</span>
            </button>
            <button className="flex flex-col items-center py-2 px-1 text-gray-400 hover:text-gray-600">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="user" className="lucide lucide-user w-5 h-5"><path d="M19 21v-2a4 4 0 0 0-4-4H9a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                <span className="text-xs mt-1">Profile</span>
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
            
            // Export Report button
            const exportBtn = document.querySelector('button:has(i[data-lucide="download"])');
            if (exportBtn) {
                exportBtn.addEventListener('click', function() {
                    console.log('Exporting BIA report...');
                    // In real implementation, trigger report download
                });
            }
            
            // Share button
            const shareBtn = document.querySelector('button:has(i[data-lucide="share"])');
            if (shareBtn) {
                shareBtn.addEventListener('click', function() {
                    console.log('Sharing BIA...');
                    // In real implementation, show share modal
                });
            }
            
            // Edit BIA button
            const editBtn = document.querySelector('button:has(i[data-lucide="edit"])');
            if (editBtn) {
                editBtn.addEventListener('click', function() {
                    console.log('Editing BIA...');
                    // In real implementation, navigate to edit mode
                });
            }
            
            // Process table interactions
            const processRows = document.querySelectorAll('tbody tr');
            processRows.forEach(row => {
                const viewDetailsBtn = row.querySelector('button');
                if (viewDetailsBtn) {
                    viewDetailsBtn.addEventListener('click', function() {
                        console.log('Viewing process details...');
                        // In real implementation, show process detail modal
                    });
                }
            });
            
            // Filter functionality
            const filterSelects = document.querySelectorAll('select');
            filterSelects.forEach(select => {
                select.addEventListener('change', function() {
                    console.log(`Filtering by: ${this.value}`);
                    // In real implementation, filter table data
                });
            });
            
            // Search functionality
            const searchInput = document.querySelector('input[placeholder="Search processes..."]');
            if (searchInput) {
                searchInput.addEventListener('input', function() {
                    const query = this.value;
                    console.log(`Searching processes for: ${query}`);
                    // In real implementation, filter processes
                });
            }
            
            // Next steps interaction
            const nextStepItems = document.querySelectorAll('.space-y-3 .flex.items-center');
            nextStepItems.forEach(item => {
                item.addEventListener('click', function() {
                    console.log('Executing next step...');
                    // In real implementation, navigate to relevant action
                });
            });
            
            // Progress bar animations
            const progressBars = document.querySelectorAll('.bg-primary-600, .bg-success-600');
            progressBars.forEach(bar => {
                const width = bar.style.width;
                bar.style.width = '0%';
                setTimeout(() => {
                    bar.style.transition = 'width 1s ease-in-out';
                    bar.style.width = width;
                }, 500);
            });
            
            // Breadcrumb navigation
            const breadcrumbLinks = document.querySelectorAll('nav[aria-label="Breadcrumb"] a');
            breadcrumbLinks.forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    console.log(`Navigating to: ${this.textContent}`);
                    // In real implementation, navigate to parent page
                });
            });
            
            // Keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                // E to edit
                if (e.key === 'e' && !e.ctrlKey && !e.metaKey && document.activeElement.tagName !== 'INPUT') {
                    editBtn?.click();
                }
                
                // Ctrl/Cmd + S to export
                if ((e.ctrlKey || e.metaKey) && e.key === 's') {
                    e.preventDefault();
                    exportBtn?.click();
                }
                
                // Tab navigation with numbers
                if (e.key >= '1' && e.key <= '6' && !e.ctrlKey && !e.metaKey && document.activeElement.tagName !== 'INPUT') {
                    const tabIndex = parseInt(e.key) - 1;
                    if (tabButtons[tabIndex]) {
                        tabButtons[tabIndex].click();
                    }
                }
            });
            
            // Auto-refresh data
            setInterval(() => {
                console.log('Refreshing BIA data...');
                // In real implementation, refresh data via API
            }, 60000); // Every minute
        });
    </script>


    </div>
  );
};

export default Untitled1;