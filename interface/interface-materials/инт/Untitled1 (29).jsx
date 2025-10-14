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
                <div className="hidden md:flex items-center space-x-2 bg-gray-100 rounded-lg px-4 py-2 w-96">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="search" className="lucide lucide-search w-4 h-4 text-gray-400"><path d="m21 21-4.34-4.34"></path><circle cx="11" cy="11" r="8"></circle></svg>
                    <input type="text" placeholder="Search across platform..." className="bg-transparent border-none outline-none text-sm flex-1" />
                    <kbd className="px-2 py-1 text-xs text-gray-500 bg-gray-200 rounded">⌘K</kbd>
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
        
        <aside className="hidden md:flex md:w-64 md:flex-col bg-white border-r border-gray-200">
            <div className="flex flex-col flex-grow pt-6 pb-4 overflow-y-auto">
                <nav className="mt-2 flex-1 px-3 space-y-1">
                    <a href="#" className="bg-primary-50 border-r-4 border-primary-600 text-primary-700 group flex items-center px-3 py-2.5 text-sm font-medium rounded-l-lg">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="home" className="lucide lucide-home text-primary-600 mr-3 h-5 w-5"><path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"></path><path d="M3 10a2 2 0 0 1 .709-1.528l7-6a2 2 0 0 1 2.582 0l7 6A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path></svg>
                        Dashboard
                    </a>
                    <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="target" className="lucide lucide-target text-gray-400 mr-3 h-5 w-5"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>
                        BCM Journey
                    </a>
                    <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bar-chart-3" className="lucide lucide-bar-chart-3 text-gray-400 mr-3 h-5 w-5"><path d="M3 3v16a2 2 0 0 0 2 2h16"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>
                        Business Impact Analysis
                    </a>
                    <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="alert-triangle" className="lucide lucide-alert-triangle text-gray-400 mr-3 h-5 w-5"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>
                        Risk Management
                    </a>
                    <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="clipboard-list" className="lucide lucide-clipboard-list text-gray-400 mr-3 h-5 w-5"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"></rect><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><path d="M12 11h4"></path><path d="M12 16h4"></path><path d="M8 11h.01"></path><path d="M8 16h.01"></path></svg>
                        BC Plans
                    </a>
                    <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="play-circle" className="lucide lucide-play-circle text-gray-400 mr-3 h-5 w-5"><path d="M9 9.003a1 1 0 0 1 1.517-.859l4.997 2.997a1 1 0 0 1 0 1.718l-4.997 2.997A1 1 0 0 1 9 14.996z"></path><circle cx="12" cy="12" r="10"></circle></svg>
                        Exercises &amp; Testing
                    </a>
                    <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check-circle" className="lucide lucide-check-circle text-gray-400 mr-3 h-5 w-5"><path d="M21.801 10A10 10 0 1 1 17 3.335"></path><path d="m9 11 3 3L22 4"></path></svg>
                        Compliance
                    </a>
                    <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="file-text" className="lucide lucide-file-text text-gray-400 mr-3 h-5 w-5"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"></path><path d="M14 2v4a2 2 0 0 0 2 2h4"></path><path d="M10 9H8"></path><path d="M16 13H8"></path><path d="M16 17H8"></path></svg>
                        Documents
                    </a>
                    <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="activity" className="lucide lucide-activity text-gray-400 mr-3 h-5 w-5"><path d="M22 12h-2.48a2 2 0 0 0-1.93 1.46l-2.35 8.36a.25.25 0 0 1-.48 0L9.24 2.18a.25.25 0 0 0-.48 0l-2.35 8.36A2 2 0 0 1 4.49 12H2"></path></svg>
                        Monitoring &amp; Analytics
                    </a>
                    <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-colors">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="users" className="lucide lucide-users text-gray-400 mr-3 h-5 w-5"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path><path d="M16 3.128a4 4 0 0 1 0 7.744"></path><path d="M22 21v-2a4 4 0 0 0-3-3.87"></path><circle cx="9" cy="7" r="4"></circle></svg>
                        Community &amp; Learning
                    </a>
                </nav>
                
                
                <div className="px-3 py-4 border-t border-gray-200 mt-4">
                    <div className="flex items-center justify-between text-xs text-gray-500">
                        <span>v2.0.0</span>
                        <button className="hover:text-gray-700">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="help-circle" className="lucide lucide-help-circle w-4 h-4"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><path d="M12 17h.01"></path></svg>
                        </button>
                    </div>
                </div>
            </div>
        </aside>

        
        <main className="flex-1 overflow-y-auto">
            <div className="py-6">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    
                    <div className="mb-8">
                        <div className="flex items-center justify-between">
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
                                <p className="mt-1 text-sm text-gray-500">Welcome back! Here's what's happening with your BCM program.</p>
                            </div>
                            <div className="flex items-center space-x-3">
                                <button className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="download" className="lucide lucide-download w-4 h-4 mr-2"><path d="M12 15V3"></path><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><path d="m7 10 5 5 5-5"></path></svg>
                                    Export Report
                                </button>
                                <button className="bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="plus" className="lucide lucide-plus w-4 h-4 mr-2"><path d="M5 12h14"></path><path d="M12 5v14"></path></svg>
                                    Quick Action
                                </button>
                            </div>
                        </div>
                    </div>

                    
                    <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl shadow-lg p-8 mb-8">
                        <div className="flex items-center justify-between">
                            <div className="flex-1">
                                <div className="flex items-center space-x-2 mb-3">
                                    <h2 className="text-2xl font-bold text-white">Good morning, Alex!</h2>
                                    <div className="w-6 h-6 bg-yellow-400 rounded-full flex items-center justify-center">
                                        <span className="text-sm">👋</span>
                                    </div>
                                </div>
                                <p className="text-primary-100 mb-6 text-lg">Your BCM journey is 68% complete. You're making excellent progress!</p>
                                <div className="flex items-center space-x-6">
                                    <div className="flex-1 max-w-md">
                                        <div className="flex justify-between text-sm text-primary-100 mb-2">
                                            <span className="font-medium">Journey Progress</span>
                                            <span className="font-bold">68%</span>
                                        </div>
                                        <div className="w-full bg-primary-500 rounded-full h-3">
                                            <div className="bg-white h-3 rounded-full transition-all duration-500" style={{width: '68%', transition: 'width 1s ease-in-out'}}></div>
                                        </div>
                                        <p className="text-xs text-primary-200 mt-2">Estimated completion: 3 weeks</p>
                                    </div>
                                    <button className="bg-white text-primary-600 px-6 py-3 rounded-lg font-medium hover:bg-primary-50 transition-colors flex items-center space-x-2">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="arrow-right" className="lucide lucide-arrow-right w-4 h-4"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg>
                                        <span>Continue Journey</span>
                                    </button>
                                </div>
                            </div>
                            <div className="hidden lg:block ml-8">
                                <div className="w-32 h-32 bg-primary-500 rounded-2xl flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="trending-up" className="lucide lucide-trending-up w-16 h-16 text-white"><path d="M16 7h6v6"></path><path d="m22 7-8.5 8.5-5-5L2 17"></path></svg>
                                </div>
                            </div>
                        </div>
                    </div>

                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-500 mb-1">Active BIAs</p>
                                    <p className="text-3xl font-bold text-gray-900">12</p>
                                    <div className="flex items-center mt-2">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="trending-up" className="lucide lucide-trending-up w-4 h-4 text-success-600 mr-1"><path d="M16 7h6v6"></path><path d="m22 7-8.5 8.5-5-5L2 17"></path></svg>
                                        <span className="text-sm font-medium text-success-600">+2 this week</span>
                                    </div>
                                </div>
                                <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bar-chart-3" className="lucide lucide-bar-chart-3 w-6 h-6 text-primary-600"><path d="M3 3v16a2 2 0 0 0 2 2h16"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-500 mb-1">Identified Risks</p>
                                    <p className="text-3xl font-bold text-gray-900">47</p>
                                    <div className="flex items-center mt-2">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="alert-circle" className="lucide lucide-alert-circle w-4 h-4 text-warning-600 mr-1"><circle cx="12" cy="12" r="10"></circle><line x1="12" x2="12" y1="8" y2="12"></line><line x1="12" x2="12.01" y1="16" y2="16"></line></svg>
                                        <span className="text-sm font-medium text-warning-600">5 high priority</span>
                                    </div>
                                </div>
                                <div className="w-12 h-12 bg-warning-100 rounded-xl flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="alert-triangle" className="lucide lucide-alert-triangle w-6 h-6 text-warning-600"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-500 mb-1">Active Plans</p>
                                    <p className="text-3xl font-bold text-gray-900">8</p>
                                    <div className="flex items-center mt-2">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check-circle" className="lucide lucide-check-circle w-4 h-4 text-success-600 mr-1"><path d="M21.801 10A10 10 0 1 1 17 3.335"></path><path d="m9 11 3 3L22 4"></path></svg>
                                        <span className="text-sm font-medium text-success-600">All approved</span>
                                    </div>
                                </div>
                                <div className="w-12 h-12 bg-success-100 rounded-xl flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="clipboard-list" className="lucide lucide-clipboard-list w-6 h-6 text-success-600"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"></rect><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><path d="M12 11h4"></path><path d="M12 16h4"></path><path d="M8 11h.01"></path><path d="M8 16h.01"></path></svg>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-500 mb-1">Compliance Score</p>
                                    <p className="text-3xl font-bold text-gray-900">82%</p>
                                    <div className="flex items-center mt-2">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="trending-up" className="lucide lucide-trending-up w-4 h-4 text-success-600 mr-1"><path d="M16 7h6v6"></path><path d="m22 7-8.5 8.5-5-5L2 17"></path></svg>
                                        <span className="text-sm font-medium text-success-600">+3% this month</span>
                                    </div>
                                </div>
                                <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="shield-check" className="lucide lucide-shield-check w-6 h-6 text-primary-600"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"></path><path d="m9 12 2 2 4-4"></path></svg>
                                </div>
                            </div>
                        </div>
                    </div>

                    
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        
                        <div className="lg:col-span-2">
                            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
                                <div className="px-6 py-5 border-b border-gray-200">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <h3 className="text-lg font-semibold text-gray-900">BCM Journey Timeline</h3>
                                            <p className="text-sm text-gray-500 mt-1">Track your progress through the BCM implementation</p>
                                        </div>
                                        <button className="text-primary-600 text-sm font-medium hover:text-primary-700">
                                            View Full Journey
                                        </button>
                                    </div>
                                </div>
                                <div className="p-6">
                                    <div className="space-y-8">
                                        
                                        <div className="flex items-start">
                                            <div className="flex-shrink-0">
                                                <div className="w-10 h-10 bg-success-600 rounded-full flex items-center justify-center">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check" className="lucide lucide-check w-5 h-5 text-white"><path d="M20 6 9 17l-5-5"></path></svg>
                                                </div>
                                            </div>
                                            <div className="ml-4 flex-1">
                                                <div className="flex items-center justify-between">
                                                    <h4 className="text-base font-semibold text-gray-900">Initial Assessment</h4>
                                                    <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">Completed</span>
                                                </div>
                                                <p className="text-sm text-gray-600 mt-1">Completed organizational readiness assessment and established BCM framework</p>
                                                <div className="flex items-center mt-2 text-xs text-gray-500">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="calendar" className="lucide lucide-calendar w-3 h-3 mr-1"><path d="M8 2v4"></path><path d="M16 2v4"></path><rect width="18" height="18" x="3" y="4" rx="2"></rect><path d="M3 10h18"></path></svg>
                                                    <span>Completed 2 weeks ago</span>
                                                    <span className="mx-2">•</span>
                                                    <span className="text-success-600 font-medium">100% Complete</span>
                                                </div>
                                            </div>
                                        </div>

                                        
                                        <div className="flex items-start">
                                            <div className="flex-shrink-0">
                                                <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center animate-pulse">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="play" className="lucide lucide-play w-5 h-5 text-white"><path d="M5 5a2 2 0 0 1 3.008-1.728l11.997 6.998a2 2 0 0 1 .003 3.458l-12 7A2 2 0 0 1 5 19z"></path></svg>
                                                </div>
                                            </div>
                                            <div className="ml-4 flex-1">
                                                <div className="flex items-center justify-between">
                                                    <h4 className="text-base font-semibold text-gray-900">Business Impact Analysis</h4>
                                                    <span className="text-xs text-primary-600 bg-primary-100 px-2 py-1 rounded-full font-medium">In Progress</span>
                                                </div>
                                                <p className="text-sm text-gray-600 mt-1">Analyzing critical business processes and their dependencies</p>
                                                <div className="mt-3">
                                                    <div className="flex justify-between text-xs text-gray-600 mb-1">
                                                        <span>Progress</span>
                                                        <span className="font-medium">75%</span>
                                                    </div>
                                                    <div className="w-full bg-gray-200 rounded-full h-2">
                                                        <div className="bg-primary-600 h-2 rounded-full transition-all duration-500" style={{width: '75%', transition: 'width 1s ease-in-out'}}></div>
                                                    </div>
                                                    <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
                                                        <span>12 of 16 processes analyzed</span>
                                                        <span>Est. completion: 3 days</span>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        
                                        <div className="flex items-start">
                                            <div className="flex-shrink-0">
                                                <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="clock" className="lucide lucide-clock w-5 h-5 text-gray-400"><path d="M12 6v6l4 2"></path><circle cx="12" cy="12" r="10"></circle></svg>
                                                </div>
                                            </div>
                                            <div className="ml-4 flex-1">
                                                <div className="flex items-center justify-between">
                                                    <h4 className="text-base font-medium text-gray-500">Risk Assessment</h4>
                                                    <span className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded-full">Upcoming</span>
                                                </div>
                                                <p className="text-sm text-gray-400 mt-1">Identify and assess business continuity risks</p>
                                                <div className="flex items-center mt-2 text-xs text-gray-400">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="calendar" className="lucide lucide-calendar w-3 h-3 mr-1"><path d="M8 2v4"></path><path d="M16 2v4"></path><rect width="18" height="18" x="3" y="4" rx="2"></rect><path d="M3 10h18"></path></svg>
                                                    <span>Estimated start: Next week</span>
                                                </div>
                                            </div>
                                        </div>

                                        <div className="flex items-start">
                                            <div className="flex-shrink-0">
                                                <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="clock" className="lucide lucide-clock w-5 h-5 text-gray-400"><path d="M12 6v6l4 2"></path><circle cx="12" cy="12" r="10"></circle></svg>
                                                </div>
                                            </div>
                                            <div className="ml-4 flex-1">
                                                <div className="flex items-center justify-between">
                                                    <h4 className="text-base font-medium text-gray-500">Plan Development</h4>
                                                    <span className="text-xs text-gray-400 bg-gray-100 px-2 py-1 rounded-full">Upcoming</span>
                                                </div>
                                                <p className="text-sm text-gray-400 mt-1">Create comprehensive business continuity plans</p>
                                                <div className="flex items-center mt-2 text-xs text-gray-400">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="calendar" className="lucide lucide-calendar w-3 h-3 mr-1"><path d="M8 2v4"></path><path d="M16 2v4"></path><rect width="18" height="18" x="3" y="4" rx="2"></rect><path d="M3 10h18"></path></svg>
                                                    <span>Estimated start: In 3 weeks</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        
                        <div className="space-y-6">
                            
                            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
                                <div className="px-6 py-5 border-b border-gray-200">
                                    <div className="flex items-center justify-between">
                                        <div className="flex items-center">
                                            <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center mr-3">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bot" className="lucide lucide-bot w-4 h-4 text-primary-600"><path d="M12 8V4H8"></path><rect width="16" height="12" x="4" y="8" rx="2"></rect><path d="M2 14h2"></path><path d="M20 14h2"></path><path d="M15 13v2"></path><path d="M9 13v2"></path></svg>
                                            </div>
                                            <h3 className="text-lg font-semibold text-gray-900">AI Recommendations</h3>
                                        </div>
                                        <span className="text-xs bg-primary-100 text-primary-600 px-2 py-1 rounded-full font-medium">3 New</span>
                                    </div>
                                </div>
                                <div className="p-6">
                                    <div className="space-y-4">
                                        <div className="border-l-4 border-primary-500 pl-4 py-2">
                                            <div className="flex items-start justify-between">
                                                <div className="flex-1">
                                                    <h4 className="text-sm font-semibold text-gray-900">Complete IT Recovery BIA</h4>
                                                    <p className="text-sm text-gray-600 mt-1">Your IT systems analysis is 60% complete. Finishing this will unlock automated plan generation.</p>
                                                </div>
                                                <span className="text-xs bg-primary-100 text-primary-600 px-2 py-1 rounded-full font-medium ml-2">High</span>
                                            </div>
                                            <button className="text-primary-600 text-sm font-medium mt-3 hover:text-primary-700 flex items-center">
                                                <span>Continue BIA</span>
                                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="arrow-right" className="lucide lucide-arrow-right w-3 h-3 ml-1"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg>
                                            </button>
                                        </div>
                                        
                                        <div className="border-l-4 border-warning-500 pl-4 py-2">
                                            <div className="flex items-start justify-between">
                                                <div className="flex-1">
                                                    <h4 className="text-sm font-semibold text-gray-900">Review High-Risk Processes</h4>
                                                    <p className="text-sm text-gray-600 mt-1">3 critical processes have RTO gaps. Review and update recovery strategies.</p>
                                                </div>
                                                <span className="text-xs bg-warning-100 text-warning-600 px-2 py-1 rounded-full font-medium ml-2">Medium</span>
                                            </div>
                                            <button className="text-warning-600 text-sm font-medium mt-3 hover:text-warning-700 flex items-center">
                                                <span>View Risks</span>
                                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="arrow-right" className="lucide lucide-arrow-right w-3 h-3 ml-1"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg>
                                            </button>
                                        </div>
                                        
                                        <div className="border-l-4 border-success-500 pl-4 py-2">
                                            <div className="flex items-start justify-between">
                                                <div className="flex-1">
                                                    <h4 className="text-sm font-semibold text-gray-900">Schedule Tabletop Exercise</h4>
                                                    <p className="text-sm text-gray-600 mt-1">Based on your current plans, it's time for a communication test exercise.</p>
                                                </div>
                                                <span className="text-xs bg-success-100 text-success-600 px-2 py-1 rounded-full font-medium ml-2">Low</span>
                                            </div>
                                            <button className="text-success-600 text-sm font-medium mt-3 hover:text-success-700 flex items-center">
                                                <span>Schedule</span>
                                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="arrow-right" className="lucide lucide-arrow-right w-3 h-3 ml-1"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            
                            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
                                <div className="px-6 py-5 border-b border-gray-200">
                                    <div className="flex items-center justify-between">
                                        <h3 className="text-lg font-semibold text-gray-900">ISO 22301 Compliance</h3>
                                        <button className="text-primary-600 text-sm font-medium hover:text-primary-700">
                                            View Details
                                        </button>
                                    </div>
                                </div>
                                <div className="p-6">
                                    <div className="text-center mb-6">
                                        <div className="relative inline-flex items-center justify-center w-28 h-28 mb-4">
                                            <svg className="w-28 h-28 transform -rotate-90" viewBox="0 0 36 36">
                                                <path className="text-gray-200" stroke="currentColor" stroke-width="2" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"></path>
                                                <path className="text-success-600" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="82, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"></path>
                                            </svg>
                                            <div className="absolute inset-0 flex items-center justify-center">
                                                <div className="text-center">
                                                    <span className="text-2xl font-bold text-gray-900">82%</span>
                                                    <p className="text-xs text-gray-500">Compliant</p>
                                                </div>
                                            </div>
                                        </div>
                                        <p className="text-sm text-gray-600">Overall Compliance Score</p>
                                        <div className="flex items-center justify-center mt-2">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="trending-up" className="lucide lucide-trending-up w-4 h-4 text-success-600 mr-1"><path d="M16 7h6v6"></path><path d="m22 7-8.5 8.5-5-5L2 17"></path></svg>
                                            <span className="text-sm text-success-600 font-medium">+3% this month</span>
                                        </div>
                                    </div>
                                    
                                    <div className="space-y-3">
                                        <div className="flex justify-between items-center py-2">
                                            <div className="flex items-center">
                                                <div className="w-2 h-2 bg-success-600 rounded-full mr-3"></div>
                                                <span className="text-sm text-gray-700">Context &amp; Leadership</span>
                                            </div>
                                            <span className="text-sm font-semibold text-success-600">95%</span>
                                        </div>
                                        <div className="flex justify-between items-center py-2">
                                            <div className="flex items-center">
                                                <div className="w-2 h-2 bg-warning-600 rounded-full mr-3"></div>
                                                <span className="text-sm text-gray-700">Planning</span>
                                            </div>
                                            <span className="text-sm font-semibold text-warning-600">78%</span>
                                        </div>
                                        <div className="flex justify-between items-center py-2">
                                            <div className="flex items-center">
                                                <div className="w-2 h-2 bg-success-600 rounded-full mr-3"></div>
                                                <span className="text-sm text-gray-700">Support &amp; Operation</span>
                                            </div>
                                            <span className="text-sm font-semibold text-success-600">85%</span>
                                        </div>
                                        <div className="flex justify-between items-center py-2">
                                            <div className="flex items-center">
                                                <div className="w-2 h-2 bg-danger-600 rounded-full mr-3"></div>
                                                <span className="text-sm text-gray-700">Performance Evaluation</span>
                                            </div>
                                            <span className="text-sm font-semibold text-danger-600">65%</span>
                                        </div>
                                    </div>
                                    
                                    <button className="w-full mt-6 bg-primary-600 text-white py-3 px-4 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors flex items-center justify-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="file-text" className="lucide lucide-file-text w-4 h-4 mr-2"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"></path><path d="M14 2v4a2 2 0 0 0 2 2h4"></path><path d="M10 9H8"></path><path d="M16 13H8"></path><path d="M16 17H8"></path></svg>
                                        Generate Compliance Report
                                    </button>
                                </div>
                            </div>

                            
                            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
                                <div className="px-6 py-5 border-b border-gray-200">
                                    <div className="flex items-center justify-between">
                                        <h3 className="text-lg font-semibold text-gray-900">Recent Activities</h3>
                                        <button className="text-primary-600 text-sm font-medium hover:text-primary-700">
                                            View All
                                        </button>
                                    </div>
                                </div>
                                <div className="p-6">
                                    <div className="space-y-4">
                                        <div className="flex items-start space-x-3">
                                            <div className="w-8 h-8 bg-success-100 rounded-full flex items-center justify-center flex-shrink-0">
                                                <span className="text-xs font-medium text-success-600">SC</span>
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <p className="text-sm text-gray-900">
                                                    <span className="font-medium">Sarah Chen</span> completed BIA for Customer Service department
                                                </p>
                                                <div className="flex items-center mt-1 text-xs text-gray-500">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="clock" className="lucide lucide-clock w-3 h-3 mr-1"><path d="M12 6v6l4 2"></path><circle cx="12" cy="12" r="10"></circle></svg>
                                                    <span>2 hours ago</span>
                                                    <span className="mx-2">•</span>
                                                    <span className="text-success-600">BIA Completed</span>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div className="flex items-start space-x-3">
                                            <div className="w-8 h-8 bg-warning-100 rounded-full flex items-center justify-center flex-shrink-0">
                                                <span className="text-xs font-medium text-warning-600">MR</span>
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <p className="text-sm text-gray-900">
                                                    <span className="font-medium">Mike Rodriguez</span> updated risk assessment for IT infrastructure
                                                </p>
                                                <div className="flex items-center mt-1 text-xs text-gray-500">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="clock" className="lucide lucide-clock w-3 h-3 mr-1"><path d="M12 6v6l4 2"></path><circle cx="12" cy="12" r="10"></circle></svg>
                                                    <span>4 hours ago</span>
                                                    <span className="mx-2">•</span>
                                                    <span className="text-warning-600">Risk Updated</span>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div className="flex items-start space-x-3">
                                            <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                                                <span className="text-xs font-medium text-primary-600">EW</span>
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <p className="text-sm text-gray-900">
                                                    <span className="font-medium">Emma Wilson</span> created new BC plan template for remote work
                                                </p>
                                                <div className="flex items-center mt-1 text-xs text-gray-500">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="clock" className="lucide lucide-clock w-3 h-3 mr-1"><path d="M12 6v6l4 2"></path><circle cx="12" cy="12" r="10"></circle></svg>
                                                    <span>1 day ago</span>
                                                    <span className="mx-2">•</span>
                                                    <span className="text-primary-600">Template Created</span>
                                                </div>
                                            </div>
                                        </div>
                                        
                                        <div className="flex items-start space-x-3">
                                            <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bot" className="lucide lucide-bot w-4 h-4 text-primary-600"><path d="M12 8V4H8"></path><rect width="16" height="12" x="4" y="8" rx="2"></rect><path d="M2 14h2"></path><path d="M20 14h2"></path><path d="M15 13v2"></path><path d="M9 13v2"></path></svg>
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <p className="text-sm text-gray-900">
                                                    <span className="font-medium">AI Assistant</span> generated compliance recommendations
                                                </p>
                                                <div className="flex items-center mt-1 text-xs text-gray-500">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="clock" className="lucide lucide-clock w-3 h-3 mr-1"><path d="M12 6v6l4 2"></path><circle cx="12" cy="12" r="10"></circle></svg>
                                                    <span>2 days ago</span>
                                                    <span className="mx-2">•</span>
                                                    <span className="text-primary-600">AI Analysis</span>
                                                </div>
                                            </div>
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
            <button className="flex flex-col items-center py-2 px-1 text-primary-600 bg-primary-50 rounded-lg">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="home" className="lucide lucide-home w-5 h-5"><path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"></path><path d="M3 10a2 2 0 0 1 .709-1.528l7-6a2 2 0 0 1 2.582 0l7 6A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path></svg>
                <span className="text-xs mt-1 font-medium">Dashboard</span>
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
            <button className="flex flex-col items-center py-2 px-1 text-gray-400 hover:text-gray-600">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="menu" className="lucide lucide-menu w-5 h-5"><path d="M4 5h16"></path><path d="M4 12h16"></path><path d="M4 19h16"></path></svg>
                <span className="text-xs mt-1">More</span>
            </button>
        </div>
    </div>

    
    <button className="fixed bottom-20 right-6 w-14 h-14 bg-primary-600 text-white rounded-full shadow-lg hover:bg-primary-700 transition-all hover:scale-105 flex items-center justify-center md:bottom-8 md:right-8">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bot" className="lucide lucide-bot w-6 h-6"><path d="M12 8V4H8"></path><rect width="16" height="12" x="4" y="8" rx="2"></rect><path d="M2 14h2"></path><path d="M20 14h2"></path><path d="M15 13v2"></path><path d="M9 13v2"></path></svg>
    </button>

    <script>
        // Initialize Lucide icons
        lucide.createIcons();
        
        // Simple interactivity
        document.addEventListener('DOMContentLoaded', function() {
            // Add click handlers for navigation
            const navLinks = document.querySelectorAll('nav a, aside a');
            navLinks.forEach(link => {
                link.addEventListener('click', function(e) {
                    e.preventDefault();
                    // Remove active state from all links
                    navLinks.forEach(l => {
                        l.classList.remove('bg-primary-50', 'border-r-4', 'border-primary-600', 'text-primary-700');
                        l.classList.add('text-gray-600');
                    });
                    // Add active state to clicked link
                    this.classList.remove('text-gray-600');
                    this.classList.add('bg-primary-50', 'border-r-4', 'border-primary-600', 'text-primary-700');
                });
            });
            
            // Animate progress bars on load
            setTimeout(() => {
                const progressBars = document.querySelectorAll('[style*="width:"]');
                progressBars.forEach(bar => {
                    bar.style.transition = 'width 1s ease-in-out';
                });
            }, 100);
        });
    </script>


    </div>
  );
};

export default Untitled1;