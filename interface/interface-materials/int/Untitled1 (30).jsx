import React from 'react';

const Untitled1 = () => {
  return (
    <div>
      
    
    <nav className="bg-white border-b border-gray-200 px-4 py-3 sm:px-6">
        <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
                <div className="flex items-center space-x-3">
                    <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="shield-check" className="lucide lucide-shield-check w-5 h-5 text-white"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"></path><path d="m9 12 2 2 4-4"></path></svg>
                    </div>
                    <h1 className="text-xl font-bold text-gray-900">AI-Platform-ISO</h1>
                </div>
                <div className="hidden md:flex items-center space-x-2 bg-gray-100 rounded-lg px-3 py-2 w-96">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="search" className="lucide lucide-search w-4 h-4 text-gray-400"><path d="m21 21-4.34-4.34"></path><circle cx="11" cy="11" r="8"></circle></svg>
                    <input type="text" placeholder="Search across platform..." className="bg-transparent border-none outline-none text-sm flex-1" />
                </div>
            </div>
            <div className="flex items-center space-x-4">
                <button className="relative p-2 text-gray-400 hover:text-gray-600">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bell" className="lucide lucide-bell w-5 h-5"><path d="M10.268 21a2 2 0 0 0 3.464 0"></path><path d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326"></path></svg>
                    <span className="absolute -top-1 -right-1 w-3 h-3 bg-danger-500 rounded-full"></span>
                </button>
                <button className="p-2 text-gray-400 hover:text-gray-600">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bot" className="lucide lucide-bot w-5 h-5"><path d="M12 8V4H8"></path><rect width="16" height="12" x="4" y="8" rx="2"></rect><path d="M2 14h2"></path><path d="M20 14h2"></path><path d="M15 13v2"></path><path d="M9 13v2"></path></svg>
                </button>
                <div className="flex items-center space-x-3">
                    <img src="https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=40&amp;h=40&amp;fit=crop&amp;crop=face" alt="User" className="w-8 h-8 rounded-full" />
                    <div className="hidden md:block">
                        <p className="text-sm font-medium text-gray-900">Alex Johnson</p>
                        <p className="text-xs text-gray-500">BCM Manager</p>
                    </div>
                </div>
            </div>
        </div>
    </nav>

    <div className="flex">
        
        <aside className="hidden md:flex md:w-64 md:flex-col">
            <div className="flex flex-col flex-grow bg-white border-r border-gray-200 pt-5 pb-4 overflow-y-auto">
                <nav className="mt-5 flex-1 px-2 space-y-1">
                    <a href="#" className="bg-primary-50 border-r-2 border-primary-600 text-primary-700 group flex items-center px-2 py-2 text-sm font-medium rounded-l-md">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="home" className="lucide lucide-home text-primary-500 mr-3 h-5 w-5"><path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"></path><path d="M3 10a2 2 0 0 1 .709-1.528l7-6a2 2 0 0 1 2.582 0l7 6A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path></svg>
                        Dashboard
                    </a>
                    <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="target" className="lucide lucide-target text-gray-400 mr-3 h-5 w-5"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>
                        BCM Journey
                    </a>
                    <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bar-chart-3" className="lucide lucide-bar-chart-3 text-gray-400 mr-3 h-5 w-5"><path d="M3 3v16a2 2 0 0 0 2 2h16"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>
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
                    <a href="#" className="text-gray-600 hover:bg-gray-50 hover:text-gray-900 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="users" className="lucide lucide-users text-gray-400 mr-3 h-5 w-5"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path><path d="M16 3.128a4 4 0 0 1 0 7.744"></path><path d="M22 21v-2a4 4 0 0 0-3-3.87"></path><circle cx="9" cy="7" r="4"></circle></svg>
                        Community
                    </a>
                </nav>
            </div>
        </aside>

        
        <main className="flex-1 overflow-y-auto">
            <div className="py-6">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 md:px-8">
                    
                    <div className="mb-8">
                        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
                        <p className="mt-1 text-sm text-gray-500">Welcome back! Here's what's happening with your BCM program.</p>
                    </div>

                    
                    <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-lg shadow-lg p-6 mb-8">
                        <div className="flex items-center justify-between">
                            <div className="flex-1">
                                <h2 className="text-xl font-bold text-white mb-2">Good morning, Alex! </h2>
                                <p className="text-primary-100 mb-4">Your BCM journey is 68% complete. You're making excellent progress!</p>
                                <div className="flex items-center space-x-4">
                                    <div className="flex-1">
                                        <div className="flex justify-between text-sm text-primary-100 mb-1">
                                            <span>Journey Progress</span>
                                            <span>68%</span>
                                        </div>
                                        <div className="w-full bg-primary-500 rounded-full h-2">
                                            <div className="bg-white h-2 rounded-full" style={{width: '68%'}}></div>
                                        </div>
                                    </div>
                                    <button className="bg-white text-primary-600 px-4 py-2 rounded-lg font-medium hover:bg-primary-50 transition-colors">
                                        Continue Journey
                                    </button>
                                </div>
                            </div>
                            <div className="hidden lg:block ml-6">
                                <img src="https://images.unsplash.com/photo-1551434678-e076c223a692?w=200&amp;h=120&amp;fit=crop" alt="BCM Journey" className="w-48 h-28 rounded-lg object-cover" />
                            </div>
                        </div>
                    </div>

                    
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                        <div className="bg-white rounded-lg shadow p-6">
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bar-chart-3" className="lucide lucide-bar-chart-3 w-5 h-5 text-primary-600"><path d="M3 3v16a2 2 0 0 0 2 2h16"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>
                                    </div>
                                </div>
                                <div className="ml-4 flex-1">
                                    <p className="text-sm font-medium text-gray-500">Active BIAs</p>
                                    <p className="text-2xl font-bold text-gray-900">12</p>
                                </div>
                                <div className="text-success-600">
                                    <span className="text-sm font-medium">+2</span>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow p-6">
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <div className="w-8 h-8 bg-warning-100 rounded-lg flex items-center justify-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="alert-triangle" className="lucide lucide-alert-triangle w-5 h-5 text-warning-600"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>
                                    </div>
                                </div>
                                <div className="ml-4 flex-1">
                                    <p className="text-sm font-medium text-gray-500">Identified Risks</p>
                                    <p className="text-2xl font-bold text-gray-900">47</p>
                                </div>
                                <div className="text-warning-600">
                                    <span className="text-sm font-medium">+5</span>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow p-6">
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <div className="w-8 h-8 bg-success-100 rounded-lg flex items-center justify-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="clipboard-list" className="lucide lucide-clipboard-list w-5 h-5 text-success-600"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"></rect><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><path d="M12 11h4"></path><path d="M12 16h4"></path><path d="M8 11h.01"></path><path d="M8 16h.01"></path></svg>
                                    </div>
                                </div>
                                <div className="ml-4 flex-1">
                                    <p className="text-sm font-medium text-gray-500">Active Plans</p>
                                    <p className="text-2xl font-bold text-gray-900">8</p>
                                </div>
                                <div className="text-success-600">
                                    <span className="text-sm font-medium">+1</span>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow p-6">
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check-circle" className="lucide lucide-check-circle w-5 h-5 text-primary-600"><path d="M21.801 10A10 10 0 1 1 17 3.335"></path><path d="m9 11 3 3L22 4"></path></svg>
                                    </div>
                                </div>
                                <div className="ml-4 flex-1">
                                    <p className="text-sm font-medium text-gray-500">Compliance Score</p>
                                    <p className="text-2xl font-bold text-gray-900">82%</p>
                                </div>
                                <div className="text-success-600">
                                    <span className="text-sm font-medium">+3%</span>
                                </div>
                            </div>
                        </div>
                    </div>

                    
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        
                        <div className="lg:col-span-2">
                            <div className="bg-white rounded-lg shadow">
                                <div className="px-6 py-4 border-b border-gray-200">
                                    <h3 className="text-lg font-medium text-gray-900">BCM Journey Timeline</h3>
                                    <p className="text-sm text-gray-500">Track your progress through the BCM implementation</p>
                                </div>
                                <div className="p-6">
                                    <div className="space-y-6">
                                        
                                        <div className="flex items-start">
                                            <div className="flex-shrink-0">
                                                <div className="w-8 h-8 bg-success-600 rounded-full flex items-center justify-center">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check" className="lucide lucide-check w-4 h-4 text-white"><path d="M20 6 9 17l-5-5"></path></svg>
                                                </div>
                                            </div>
                                            <div className="ml-4 flex-1">
                                                <h4 className="text-sm font-medium text-gray-900">Initial Assessment</h4>
                                                <p className="text-sm text-gray-500">Completed organizational readiness assessment</p>
                                                <p className="text-xs text-gray-400 mt-1">Completed 2 weeks ago</p>
                                            </div>
                                        </div>

                                        
                                        <div className="flex items-start">
                                            <div className="flex-shrink-0">
                                                <div className="w-8 h-8 bg-primary-600 rounded-full flex items-center justify-center animate-pulse">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="play" className="lucide lucide-play w-4 h-4 text-white"><path d="M5 5a2 2 0 0 1 3.008-1.728l11.997 6.998a2 2 0 0 1 .003 3.458l-12 7A2 2 0 0 1 5 19z"></path></svg>
                                                </div>
                                            </div>
                                            <div className="ml-4 flex-1">
                                                <h4 className="text-sm font-medium text-gray-900">Business Impact Analysis</h4>
                                                <p className="text-sm text-gray-500">Analyzing critical business processes and dependencies</p>
                                                <div className="mt-2">
                                                    <div className="flex justify-between text-xs text-gray-500 mb-1">
                                                        <span>Progress</span>
                                                        <span>75%</span>
                                                    </div>
                                                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                                                        <div className="bg-primary-600 h-1.5 rounded-full" style={{width: '75%'}}></div>
                                                    </div>
                                                </div>
                                            </div>
                                        </div>

                                        
                                        <div className="flex items-start">
                                            <div className="flex-shrink-0">
                                                <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="clock" className="lucide lucide-clock w-4 h-4 text-gray-500"><path d="M12 6v6l4 2"></path><circle cx="12" cy="12" r="10"></circle></svg>
                                                </div>
                                            </div>
                                            <div className="ml-4 flex-1">
                                                <h4 className="text-sm font-medium text-gray-500">Risk Assessment</h4>
                                                <p className="text-sm text-gray-400">Identify and assess business continuity risks</p>
                                                <p className="text-xs text-gray-400 mt-1">Estimated start: Next week</p>
                                            </div>
                                        </div>

                                        <div className="flex items-start">
                                            <div className="flex-shrink-0">
                                                <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="clock" className="lucide lucide-clock w-4 h-4 text-gray-500"><path d="M12 6v6l4 2"></path><circle cx="12" cy="12" r="10"></circle></svg>
                                                </div>
                                            </div>
                                            <div className="ml-4 flex-1">
                                                <h4 className="text-sm font-medium text-gray-500">Plan Development</h4>
                                                <p className="text-sm text-gray-400">Create comprehensive business continuity plans</p>
                                                <p className="text-xs text-gray-400 mt-1">Estimated start: In 3 weeks</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        
                        <div className="space-y-6">
                            
                            <div className="bg-white rounded-lg shadow">
                                <div className="px-6 py-4 border-b border-gray-200">
                                    <div className="flex items-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bot" className="lucide lucide-bot w-5 h-5 text-primary-600 mr-2"><path d="M12 8V4H8"></path><rect width="16" height="12" x="4" y="8" rx="2"></rect><path d="M2 14h2"></path><path d="M20 14h2"></path><path d="M15 13v2"></path><path d="M9 13v2"></path></svg>
                                        <h3 className="text-lg font-medium text-gray-900">AI Recommendations</h3>
                                    </div>
                                </div>
                                <div className="p-6">
                                    <div className="space-y-4">
                                        <div className="border-l-4 border-primary-500 pl-4">
                                            <h4 className="text-sm font-medium text-gray-900">Complete IT Recovery BIA</h4>
                                            <p className="text-sm text-gray-600 mt-1">Your IT systems analysis is 60% complete. Finishing this will unlock automated plan generation.</p>
                                            <button className="text-primary-600 text-sm font-medium mt-2 hover:text-primary-700">Continue BIA →</button>
                                        </div>
                                        <div className="border-l-4 border-warning-500 pl-4">
                                            <h4 className="text-sm font-medium text-gray-900">Review High-Risk Processes</h4>
                                            <p className="text-sm text-gray-600 mt-1">3 critical processes have RTO gaps. Review and update recovery strategies.</p>
                                            <button className="text-warning-600 text-sm font-medium mt-2 hover:text-warning-700">View Risks →</button>
                                        </div>
                                        <div className="border-l-4 border-success-500 pl-4">
                                            <h4 className="text-sm font-medium text-gray-900">Schedule Tabletop Exercise</h4>
                                            <p className="text-sm text-gray-600 mt-1">Based on your current plans, it's time for a communication test exercise.</p>
                                            <button className="text-success-600 text-sm font-medium mt-2 hover:text-success-700">Schedule →</button>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            
                            <div className="bg-white rounded-lg shadow">
                                <div className="px-6 py-4 border-b border-gray-200">
                                    <h3 className="text-lg font-medium text-gray-900">ISO 22301 Compliance</h3>
                                </div>
                                <div className="p-6">
                                    <div className="text-center mb-6">
                                        <div className="relative inline-flex items-center justify-center w-24 h-24">
                                            <svg className="w-24 h-24 transform -rotate-90" viewBox="0 0 36 36">
                                                <path className="text-gray-200" stroke="currentColor" stroke-width="3" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"></path>
                                                <path className="text-success-600" stroke="currentColor" stroke-width="3" fill="none" stroke-dasharray="82, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"></path>
                                            </svg>
                                            <div className="absolute inset-0 flex items-center justify-center">
                                                <span className="text-2xl font-bold text-gray-900">82%</span>
                                            </div>
                                        </div>
                                        <p className="text-sm text-gray-500 mt-2">Overall Compliance Score</p>
                                    </div>
                                    <div className="space-y-3">
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm text-gray-600">Context &amp; Leadership</span>
                                            <span className="text-sm font-medium text-success-600">95%</span>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm text-gray-600">Planning</span>
                                            <span className="text-sm font-medium text-warning-600">78%</span>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm text-gray-600">Support &amp; Operation</span>
                                            <span className="text-sm font-medium text-success-600">85%</span>
                                        </div>
                                        <div className="flex justify-between items-center">
                                            <span className="text-sm text-gray-600">Performance Evaluation</span>
                                            <span className="text-sm font-medium text-danger-600">65%</span>
                                        </div>
                                    </div>
                                    <button className="w-full mt-4 bg-primary-600 text-white py-2 px-4 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors">
                                        View Detailed Report
                                    </button>
                                </div>
                            </div>

                            
                            <div className="bg-white rounded-lg shadow">
                                <div className="px-6 py-4 border-b border-gray-200">
                                    <h3 className="text-lg font-medium text-gray-900">Recent Activities</h3>
                                </div>
                                <div className="p-6">
                                    <div className="space-y-4">
                                        <div className="flex items-start space-x-3">
                                            <img src="https://images.unsplash.com/photo-1494790108755-2616b612b786?w=32&amp;h=32&amp;fit=crop&amp;crop=face" alt="User" className="w-8 h-8 rounded-full" />
                                            <div className="flex-1 min-w-0">
                                                <p className="text-sm text-gray-900"><span className="font-medium">Sarah Chen</span> completed BIA for Customer Service</p>
                                                <p className="text-xs text-gray-500">2 hours ago</p>
                                            </div>
                                        </div>
                                        <div className="flex items-start space-x-3">
                                            <img src="https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=32&amp;h=32&amp;fit=crop&amp;crop=face" alt="User" className="w-8 h-8 rounded-full" />
                                            <div className="flex-1 min-w-0">
                                                <p className="text-sm text-gray-900"><span className="font-medium">Mike Rodriguez</span> updated risk assessment</p>
                                                <p className="text-xs text-gray-500">4 hours ago</p>
                                            </div>
                                        </div>
                                        <div className="flex items-start space-x-3">
                                            <img src="https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=32&amp;h=32&amp;fit=crop&amp;crop=face" alt="User" className="w-8 h-8 rounded-full" />
                                            <div className="flex-1 min-w-0">
                                                <p className="text-sm text-gray-900"><span className="font-medium">Emma Wilson</span> created new BC plan template</p>
                                                <p className="text-xs text-gray-500">1 day ago</p>
                                            </div>
                                        </div>
                                        <div className="flex items-start space-x-3">
                                            <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bot" className="lucide lucide-bot w-4 h-4 text-primary-600"><path d="M12 8V4H8"></path><rect width="16" height="12" x="4" y="8" rx="2"></rect><path d="M2 14h2"></path><path d="M20 14h2"></path><path d="M15 13v2"></path><path d="M9 13v2"></path></svg>
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <p className="text-sm text-gray-900"><span className="font-medium">AI Assistant</span> generated compliance recommendations</p>
                                                <p className="text-xs text-gray-500">2 days ago</p>
                                            </div>
                                        </div>
                                    </div>
                                    <button className="w-full mt-4 text-primary-600 text-sm font-medium hover:text-primary-700">
                                        View All Activities
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </main>
    </div>

    
    <div className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200">
        <div className="grid grid-cols-5 py-2">
            <button className="flex flex-col items-center py-2 text-primary-600">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="home" className="lucide lucide-home w-5 h-5"><path d="M15 21v-8a1 1 0 0 0-1-1h-4a1 1 0 0 0-1 1v8"></path><path d="M3 10a2 2 0 0 1 .709-1.528l7-6a2 2 0 0 1 2.582 0l7 6A2 2 0 0 1 21 10v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path></svg>
                <span className="text-xs mt-1">Home</span>
            </button>
            <button className="flex flex-col items-center py-2 text-gray-400">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bar-chart-3" className="lucide lucide-bar-chart-3 w-5 h-5"><path d="M3 3v16a2 2 0 0 0 2 2h16"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>
                <span className="text-xs mt-1">BIA</span>
            </button>
            <button className="flex flex-col items-center py-2 text-gray-400">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="alert-triangle" className="lucide lucide-alert-triangle w-5 h-5"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>
                <span className="text-xs mt-1">Risks</span>
            </button>
            <button className="flex flex-col items-center py-2 text-gray-400">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="clipboard-list" className="lucide lucide-clipboard-list w-5 h-5"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"></rect><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><path d="M12 11h4"></path><path d="M12 16h4"></path><path d="M8 11h.01"></path><path d="M8 16h.01"></path></svg>
                <span className="text-xs mt-1">Plans</span>
            </button>
            <button className="flex flex-col items-center py-2 text-gray-400">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="menu" className="lucide lucide-menu w-5 h-5"><path d="M4 5h16"></path><path d="M4 12h16"></path><path d="M4 19h16"></path></svg>
                <span className="text-xs mt-1">More</span>
            </button>
        </div>
    </div>

    
    <button className="fixed bottom-6 right-6 w-14 h-14 bg-primary-600 text-white rounded-full shadow-lg hover:bg-primary-700 transition-colors flex items-center justify-center md:bottom-8 md:right-8">
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
                    navLinks.forEach(l => l.classList.remove('bg-primary-50', 'border-r-2', 'border-primary-600', 'text-primary-700'));
                    // Add active state to clicked link
                    this.classList.add('bg-primary-50', 'border-r-2', 'border-primary-600', 'text-primary-700');
                });
            });
        });
    </script>


    </div>
  );
};

export default Untitled1;