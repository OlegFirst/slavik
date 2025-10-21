import React from 'react';

const Untitled1 = () => {
  return (
    <div>
      
    
    <header className="bg-white border-b border-gray-200 px-4 py-3 sticky top-0 z-10">
        <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
                <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="shield-check" className="lucide lucide-shield-check w-5 h-5 text-white"><path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"></path><path d="m9 12 2 2 4-4"></path></svg>
                </div>
                <div>
                    <h1 className="text-lg font-bold text-gray-900">BCM Platform</h1>
                    <p className="text-xs text-gray-500">AI-Platform-ISO</p>
                </div>
            </div>
            <div className="flex items-center space-x-2">
                <button className="relative p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors" style={{minHeight: '44px', minWidth: '44px'}}>
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="search" className="lucide lucide-search w-5 h-5"><path d="m21 21-4.34-4.34"></path><circle cx="11" cy="11" r="8"></circle></svg>
                </button>
                <button className="relative p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors" style={{minHeight: '44px', minWidth: '44px'}}>
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bell" className="lucide lucide-bell w-5 h-5"><path d="M10.268 21a2 2 0 0 0 3.464 0"></path><path d="M3.262 15.326A1 1 0 0 0 4 17h16a1 1 0 0 0 .74-1.673C19.41 13.956 18 12.499 18 8A6 6 0 0 0 6 8c0 4.499-1.411 5.956-2.738 7.326"></path></svg>
                    <div className="absolute -top-1 -right-1 w-3 h-3 bg-danger-500 rounded-full"></div>
                </button>
                <button className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg transition-colors" style={{minHeight: '44px', minWidth: '44px'}}>
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bot" className="lucide lucide-bot w-5 h-5"><path d="M12 8V4H8"></path><rect width="16" height="12" x="4" y="8" rx="2"></rect><path d="M2 14h2"></path><path d="M20 14h2"></path><path d="M15 13v2"></path><path d="M9 13v2"></path></svg>
                </button>
            </div>
        </div>
    </header>

    
    <main className="px-4 py-6 space-y-6">
        
        <div className="bg-gradient-to-r from-primary-600 to-primary-700 rounded-xl p-6 text-white">
            <div className="flex items-start justify-between">
                <div>
                    <h2 className="text-xl font-bold mb-2">Good morning, John!</h2>
                    <p className="text-primary-100 text-sm mb-4">Your BCM journey is 68% complete</p>
                    <div className="w-full bg-primary-500 rounded-full h-2 mb-3">
                        <div className="bg-white h-2 rounded-full" style={{width: '68%'}}></div>
                    </div>
                    <p className="text-primary-100 text-xs">Next: Complete Risk Assessment</p>
                </div>
                <div className="w-16 h-16 bg-primary-500 rounded-full flex items-center justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="target" className="lucide lucide-target w-8 h-8 text-white"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>
                </div>
            </div>
        </div>

        
        <div className="grid grid-cols-2 gap-4">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <div className="flex items-center justify-between">
                    <div>
                        <p className="text-xs font-medium text-gray-600 uppercase tracking-wide">Active BIAs</p>
                        <p className="text-2xl font-bold text-blue-600 mt-1">3</p>
                    </div>
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bar-chart-3" className="lucide lucide-bar-chart-3 w-5 h-5 text-blue-600"><path d="M3 3v16a2 2 0 0 0 2 2h16"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>
                    </div>
                </div>
                <div className="mt-3">
                    <span className="text-xs text-green-600 font-medium">+2 this week</span>
                </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <div className="flex items-center justify-between">
                    <div>
                        <p className="text-xs font-medium text-gray-600 uppercase tracking-wide">Open Risks</p>
                        <p className="text-2xl font-bold text-red-600 mt-1">12</p>
                    </div>
                    <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="alert-triangle" className="lucide lucide-alert-triangle w-5 h-5 text-red-600"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>
                    </div>
                </div>
                <div className="mt-3">
                    <span className="text-xs text-red-600 font-medium">3 high priority</span>
                </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <div className="flex items-center justify-between">
                    <div>
                        <p className="text-xs font-medium text-gray-600 uppercase tracking-wide">BC Plans</p>
                        <p className="text-2xl font-bold text-green-600 mt-1">8</p>
                    </div>
                    <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="clipboard-list" className="lucide lucide-clipboard-list w-5 h-5 text-green-600"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"></rect><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><path d="M12 11h4"></path><path d="M12 16h4"></path><path d="M8 11h.01"></path><path d="M8 16h.01"></path></svg>
                    </div>
                </div>
                <div className="mt-3">
                    <span className="text-xs text-green-600 font-medium">All active</span>
                </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <div className="flex items-center justify-between">
                    <div>
                        <p className="text-xs font-medium text-gray-600 uppercase tracking-wide">Compliance</p>
                        <p className="text-2xl font-bold text-yellow-600 mt-1">84%</p>
                    </div>
                    <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check-circle" className="lucide lucide-check-circle w-5 h-5 text-yellow-600"><path d="M21.801 10A10 10 0 1 1 17 3.335"></path><path d="m9 11 3 3L22 4"></path></svg>
                    </div>
                </div>
                <div className="mt-3">
                    <span className="text-xs text-yellow-600 font-medium">ISO 22301</span>
                </div>
            </div>
        </div>

        
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <div className="flex items-start space-x-3">
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bot" className="lucide lucide-bot w-4 h-4 text-blue-600"><path d="M12 8V4H8"></path><rect width="16" height="12" x="4" y="8" rx="2"></rect><path d="M2 14h2"></path><path d="M20 14h2"></path><path d="M15 13v2"></path><path d="M9 13v2"></path></svg>
                </div>
                <div className="flex-1">
                    <h3 className="text-sm font-medium text-blue-900 mb-2">AI Recommendations</h3>
                    <div className="space-y-2">
                        <div className="bg-white rounded-lg p-3 border border-blue-100">
                            <p className="text-sm text-blue-800 font-medium">Complete Risk Assessment for IT Systems</p>
                            <p className="text-xs text-blue-600 mt-1">High priority - Due in 3 days</p>
                            <button className="mt-2 text-xs text-blue-600 font-medium" style={{minHeight: '44px', minWidth: '44px'}}>Start Now →</button>
                        </div>
                        <div className="bg-white rounded-lg p-3 border border-blue-100">
                            <p className="text-sm text-blue-800 font-medium">Schedule Quarterly Exercise</p>
                            <p className="text-xs text-blue-600 mt-1">Recommended for Q4 2024</p>
                            <button className="mt-2 text-xs text-blue-600 font-medium" style={{minHeight: '44px', minWidth: '44px'}}>Schedule →</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-4 py-3 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Recent Activities</h3>
            </div>
            <div className="divide-y divide-gray-200">
                <div className="px-4 py-3 flex items-start space-x-3">
                    <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check-circle" className="lucide lucide-check-circle w-4 h-4 text-green-600"><path d="M21.801 10A10 10 0 1 1 17 3.335"></path><path d="m9 11 3 3L22 4"></path></svg>
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-sm text-gray-900">BIA for Finance Department completed</p>
                        <p className="text-xs text-gray-500 mt-1">Sarah Johnson • 2 hours ago</p>
                    </div>
                </div>
                
                <div className="px-4 py-3 flex items-start space-x-3">
                    <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="plus-circle" className="lucide lucide-plus-circle w-4 h-4 text-blue-600"><circle cx="12" cy="12" r="10"></circle><path d="M8 12h8"></path><path d="M12 8v8"></path></svg>
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-sm text-gray-900">New risk added: Cyber Security Threat</p>
                        <p className="text-xs text-gray-500 mt-1">Mike Rodriguez • 4 hours ago</p>
                    </div>
                </div>
                
                <div className="px-4 py-3 flex items-start space-x-3">
                    <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="play-circle" className="lucide lucide-play-circle w-4 h-4 text-purple-600"><path d="M9 9.003a1 1 0 0 1 1.517-.859l4.997 2.997a1 1 0 0 1 0 1.718l-4.997 2.997A1 1 0 0 1 9 14.996z"></path><circle cx="12" cy="12" r="10"></circle></svg>
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-sm text-gray-900">Exercise simulation completed</p>
                        <p className="text-xs text-gray-500 mt-1">David Wilson • Yesterday</p>
                    </div>
                </div>
                
                <div className="px-4 py-3 flex items-start space-x-3">
                    <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center flex-shrink-0">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="edit" className="lucide lucide-edit w-4 h-4 text-yellow-600"><path d="M12 3H5a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.375 2.625a1 1 0 0 1 3 3l-9.013 9.014a2 2 0 0 1-.853.505l-2.873.84a.5.5 0 0 1-.62-.62l.84-2.873a2 2 0 0 1 .506-.852z"></path></svg>
                    </div>
                    <div className="flex-1 min-w-0">
                        <p className="text-sm text-gray-900">IT Recovery Plan updated</p>
                        <p className="text-xs text-gray-500 mt-1">Anna Lee • 2 days ago</p>
                    </div>
                </div>
            </div>
            <div className="px-4 py-3 border-t border-gray-200">
                <button className="text-sm text-primary-600 font-medium" style={{minHeight: '44px', minWidth: '44px'}}>View All Activities →</button>
            </div>
        </div>

        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-4 py-3 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Quick Actions</h3>
            </div>
            <div className="p-4">
                <div className="grid grid-cols-2 gap-3">
                    <button className="flex flex-col items-center p-4 bg-blue-50 hover:bg-blue-100 rounded-lg transition-colors">
                        <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mb-2">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="plus" className="lucide lucide-plus w-5 h-5 text-blue-600"><path d="M5 12h14"></path><path d="M12 5v14"></path></svg>
                        </div>
                        <span className="text-sm font-medium text-blue-900">Start BIA</span>
                    </button>
                    
                    <button className="flex flex-col items-center p-4 bg-red-50 hover:bg-red-100 rounded-lg transition-colors">
                        <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center mb-2">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="alert-triangle" className="lucide lucide-alert-triangle w-5 h-5 text-red-600"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>
                        </div>
                        <span className="text-sm font-medium text-red-900">Add Risk</span>
                    </button>
                    
                    <button className="flex flex-col items-center p-4 bg-green-50 hover:bg-green-100 rounded-lg transition-colors">
                        <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mb-2">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="clipboard-list" className="lucide lucide-clipboard-list w-5 h-5 text-green-600"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"></rect><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><path d="M12 11h4"></path><path d="M12 16h4"></path><path d="M8 11h.01"></path><path d="M8 16h.01"></path></svg>
                        </div>
                        <span className="text-sm font-medium text-green-900">Create Plan</span>
                    </button>
                    
                    <button className="flex flex-col items-center p-4 bg-purple-50 hover:bg-purple-100 rounded-lg transition-colors">
                        <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mb-2">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="play-circle" className="lucide lucide-play-circle w-5 h-5 text-purple-600"><path d="M9 9.003a1 1 0 0 1 1.517-.859l4.997 2.997a1 1 0 0 1 0 1.718l-4.997 2.997A1 1 0 0 1 9 14.996z"></path><circle cx="12" cy="12" r="10"></circle></svg>
                        </div>
                        <span className="text-sm font-medium text-purple-900">Run Exercise</span>
                    </button>
                </div>
            </div>
        </div>

        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-4 py-3 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">ISO 22301 Compliance</h3>
            </div>
            <div className="p-4">
                <div className="flex items-center justify-center mb-4">
                    <div className="relative w-24 h-24">
                        <svg className="w-24 h-24 transform -rotate-90" viewBox="0 0 36 36">
                            <path className="text-gray-200" stroke="currentColor" stroke-width="3" fill="none" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"></path>
                            <path className="text-yellow-500" stroke="currentColor" stroke-width="3" fill="none" stroke-dasharray="84, 100" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"></path>
                        </svg>
                        <div className="absolute inset-0 flex items-center justify-center">
                            <span className="text-xl font-bold text-yellow-600">84%</span>
                        </div>
                    </div>
                </div>
                
                <div className="space-y-3">
                    <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Context &amp; Leadership</span>
                        <div className="flex items-center space-x-2">
                            <div className="w-16 bg-gray-200 rounded-full h-2">
                                <div className="bg-green-500 h-2 rounded-full" style={{width: '90%', transition: 'width 1s ease-in-out'}}></div>
                            </div>
                            <span className="text-xs text-gray-500 w-8">90%</span>
                        </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Planning</span>
                        <div className="flex items-center space-x-2">
                            <div className="w-16 bg-gray-200 rounded-full h-2">
                                <div className="bg-yellow-500 h-2 rounded-full" style={{width: '75%', transition: 'width 1s ease-in-out'}}></div>
                            </div>
                            <span className="text-xs text-gray-500 w-8">75%</span>
                        </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Support &amp; Operation</span>
                        <div className="flex items-center space-x-2">
                            <div className="w-16 bg-gray-200 rounded-full h-2">
                                <div className="bg-green-500 h-2 rounded-full" style={{width: '85%', transition: 'width 1s ease-in-out'}}></div>
                            </div>
                            <span className="text-xs text-gray-500 w-8">85%</span>
                        </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Performance Evaluation</span>
                        <div className="flex items-center space-x-2">
                            <div className="w-16 bg-gray-200 rounded-full h-2">
                                <div className="bg-red-500 h-2 rounded-full" style={{width: '60%', transition: 'width 1s ease-in-out'}}></div>
                            </div>
                            <span className="text-xs text-gray-500 w-8">60%</span>
                        </div>
                    </div>
                    
                    <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-600">Improvement</span>
                        <div className="flex items-center space-x-2">
                            <div className="w-16 bg-gray-200 rounded-full h-2">
                                <div className="bg-yellow-500 h-2 rounded-full" style={{width: '70%', transition: 'width 1s ease-in-out'}}></div>
                            </div>
                            <span className="text-xs text-gray-500 w-8">70%</span>
                        </div>
                    </div>
                </div>
                
                <div className="mt-4 pt-4 border-t border-gray-200">
                    <button className="w-full text-sm text-primary-600 font-medium" style={{minHeight: '44px', minWidth: '44px'}}>View Detailed Report →</button>
                </div>
            </div>
        </div>

        
        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
            <div className="px-4 py-3 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">System Status</h3>
            </div>
            <div className="p-4">
                <div className="grid grid-cols-2 gap-4">
                    <div className="text-center">
                        <div className="w-3 h-3 bg-green-500 rounded-full mx-auto mb-2" style={{transition: 'width 1s ease-in-out'}}></div>
                        <p className="text-xs text-gray-600">All Services</p>
                        <p className="text-sm font-medium text-green-600">Operational</p>
                    </div>
                    
                    <div className="text-center">
                        <div className="w-3 h-3 bg-green-500 rounded-full mx-auto mb-2" style={{transition: 'width 1s ease-in-out'}}></div>
                        <p className="text-xs text-gray-600">Database</p>
                        <p className="text-sm font-medium text-green-600">Healthy</p>
                    </div>
                    
                    <div className="text-center">
                        <div className="w-3 h-3 bg-yellow-500 rounded-full mx-auto mb-2" style={{transition: 'width 1s ease-in-out'}}></div>
                        <p className="text-xs text-gray-600">API Response</p>
                        <p className="text-sm font-medium text-yellow-600">245ms</p>
                    </div>
                    
                    <div className="text-center">
                        <div className="w-3 h-3 bg-green-500 rounded-full mx-auto mb-2" style={{transition: 'width 1s ease-in-out'}}></div>
                        <p className="text-xs text-gray-600">Uptime</p>
                        <p className="text-sm font-medium text-green-600">99.9%</p>
                    </div>
                </div>
            </div>
        </div>
    </main>

    
    <nav className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 px-2 py-2 z-20">
        <div className="grid grid-cols-5 gap-1">
            <button className="flex flex-col items-center py-2 px-1 text-primary-600 bg-primary-50 rounded-lg">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="layout-dashboard" className="lucide lucide-layout-dashboard w-5 h-5"><rect width="7" height="9" x="3" y="3" rx="1"></rect><rect width="7" height="5" x="14" y="3" rx="1"></rect><rect width="7" height="9" x="14" y="12" rx="1"></rect><rect width="7" height="5" x="3" y="16" rx="1"></rect></svg>
                <span className="text-xs mt-1 font-medium">Dashboard</span>
            </button>
            
            <button className="flex flex-col items-center py-2 px-1 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-lg transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bar-chart-3" className="lucide lucide-bar-chart-3 w-5 h-5"><path d="M3 3v16a2 2 0 0 0 2 2h16"></path><path d="M18 17V9"></path><path d="M13 17V5"></path><path d="M8 17v-3"></path></svg>
                <span className="text-xs mt-1">BIA</span>
            </button>
            
            <button className="flex flex-col items-center py-2 px-1 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-lg transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="alert-triangle" className="lucide lucide-alert-triangle w-5 h-5"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"></path><path d="M12 9v4"></path><path d="M12 17h.01"></path></svg>
                <span className="text-xs mt-1">Risks</span>
            </button>
            
            <button className="flex flex-col items-center py-2 px-1 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-lg transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="clipboard-list" className="lucide lucide-clipboard-list w-5 h-5"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"></rect><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path><path d="M12 11h4"></path><path d="M12 16h4"></path><path d="M8 11h.01"></path><path d="M8 16h.01"></path></svg>
                <span className="text-xs mt-1">Plans</span>
            </button>
            
            <button className="flex flex-col items-center py-2 px-1 text-gray-400 hover:text-gray-600 hover:bg-gray-50 rounded-lg transition-colors">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="menu" className="lucide lucide-menu w-5 h-5"><path d="M4 5h16"></path><path d="M4 12h16"></path><path d="M4 19h16"></path></svg>
                <span className="text-xs mt-1">More</span>
            </button>
        </div>
    </nav>

    
    <button className="fixed bottom-24 right-4 w-14 h-14 bg-primary-600 hover:bg-primary-700 text-white rounded-full shadow-lg flex items-center justify-center transition-all duration-200 hover:scale-105 z-30">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bot" className="lucide lucide-bot w-6 h-6"><path d="M12 8V4H8"></path><rect width="16" height="12" x="4" y="8" rx="2"></rect><path d="M2 14h2"></path><path d="M20 14h2"></path><path d="M15 13v2"></path><path d="M9 13v2"></path></svg>
    </button>

    
    <div className="fixed top-16 left-1/2 transform -translate-x-1/2 bg-primary-600 text-white px-4 py-2 rounded-full text-sm font-medium opacity-0 transition-opacity duration-200" id="refreshIndicator">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="refresh-cw" className="lucide lucide-refresh-cw w-4 h-4 inline mr-2"><path d="M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8"></path><path d="M21 3v5h-5"></path><path d="M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16"></path><path d="M8 16H3v5"></path></svg>
        Refreshing...
    </div>

    <script>
        // Initialize Lucide icons
        lucide.createIcons();
        
        document.addEventListener('DOMContentLoaded', function() {
            // Bottom navigation
            const navButtons = document.querySelectorAll('nav button');
            navButtons.forEach(button => {
                button.addEventListener('click', function() {
                    // Remove active state from all buttons
                    navButtons.forEach(btn => {
                        btn.classList.remove('text-primary-600', 'bg-primary-50');
                        btn.classList.add('text-gray-400');
                        btn.querySelector('span').classList.remove('font-medium');
                    });
                    
                    // Add active state to clicked button
                    this.classList.remove('text-gray-400');
                    this.classList.add('text-primary-600', 'bg-primary-50');
                    this.querySelector('span').classList.add('font-medium');
                    
                    const page = this.querySelector('span').textContent;
                    console.log(`Navigating to: ${page}`);
                    // In real implementation, navigate to page
                });
            });
            
            // Quick action buttons
            const quickActionBtns = document.querySelectorAll('.grid.grid-cols-2.gap-3 button');
            quickActionBtns.forEach(btn => {
                btn.addEventListener('click', function() {
                    const action = this.querySelector('span').textContent;
                    console.log(`Quick action: ${action}`);
                    
                    // Add visual feedback
                    this.style.transform = 'scale(0.95)';
                    setTimeout(() => {
                        this.style.transform = 'scale(1)';
                    }, 150);
                    
                    // In real implementation, navigate to specific action
                });
            });
            
            // AI recommendations
            const aiRecommendationBtns = document.querySelectorAll('.bg-blue-50 button');
            aiRecommendationBtns.forEach(btn => {
                btn.addEventListener('click', function() {
                    console.log('Following AI recommendation...');
                    // In real implementation, execute recommendation
                });
            });
            
            // Recent activities
            const activityItems = document.querySelectorAll('.divide-y > div');
            activityItems.forEach(item => {
                item.addEventListener('click', function() {
                    console.log('Viewing activity details...');
                    // In real implementation, show activity details
                });
            });
            
            // Header buttons
            const searchBtn = document.querySelector('button:has(i[data-lucide="search"])');
            const notificationBtn = document.querySelector('button:has(i[data-lucide="bell"])');
            const aiBtn = document.querySelector('button:has(i[data-lucide="bot"])');
            
            searchBtn?.addEventListener('click', function() {
                console.log('Opening search...');
                // In real implementation, open search modal
            });
            
            notificationBtn?.addEventListener('click', function() {
                console.log('Opening notifications...');
                // In real implementation, show notifications
            });
            
            aiBtn?.addEventListener('click', function() {
                console.log('Opening AI assistant...');
                // In real implementation, open AI chat
            });
            
            // AI Assistant floating button
            const aiFloatingBtn = document.querySelector('.fixed.bottom-24.right-4');
            aiFloatingBtn?.addEventListener('click', function() {
                console.log('Opening AI assistant chat...');
                // In real implementation, open AI chat panel
            });
            
            // Compliance progress bars animation
            const progressBars = document.querySelectorAll('.bg-green-500, .bg-yellow-500, .bg-red-500');
            setTimeout(() => {
                progressBars.forEach(bar => {
                    const width = bar.style.width;
                    bar.style.width = '0%';
                    bar.style.transition = 'width 1s ease-in-out';
                    setTimeout(() => {
                        bar.style.width = width;
                    }, 100);
                });
            }, 500);
            
            // Pull to refresh simulation
            let startY = 0;
            let currentY = 0;
            let isPulling = false;
            
            document.addEventListener('touchstart', function(e) {
                if (window.scrollY === 0) {
                    startY = e.touches[0].clientY;
                    isPulling = true;
                }
            });
            
            document.addEventListener('touchmove', function(e) {
                if (isPulling && window.scrollY === 0) {
                    currentY = e.touches[0].clientY;
                    const pullDistance = currentY - startY;
                    
                    if (pullDistance > 100) {
                        const indicator = document.getElementById('refreshIndicator');
                        indicator.style.opacity = '1';
                    }
                }
            });
            
            document.addEventListener('touchend', function(e) {
                if (isPulling) {
                    const pullDistance = currentY - startY;
                    
                    if (pullDistance > 100) {
                        // Trigger refresh
                        console.log('Refreshing data...');
                        setTimeout(() => {
                            const indicator = document.getElementById('refreshIndicator');
                            indicator.style.opacity = '0';
                        }, 2000);
                    }
                    
                    isPulling = false;
                    startY = 0;
                    currentY = 0;
                }
            });
            
            // Swipe gestures for navigation
            let touchStartX = 0;
            let touchEndX = 0;
            
            document.addEventListener('touchstart', function(e) {
                touchStartX = e.changedTouches[0].screenX;
            });
            
            document.addEventListener('touchend', function(e) {
                touchEndX = e.changedTouches[0].screenX;
                handleSwipe();
            });
            
            function handleSwipe() {
                const swipeThreshold = 100;
                const diff = touchStartX - touchEndX;
                
                if (Math.abs(diff) > swipeThreshold) {
                    if (diff > 0) {
                        // Swipe left - next page
                        console.log('Swiped left - next page');
                    } else {
                        // Swipe right - previous page
                        console.log('Swiped right - previous page');
                    }
                }
            }
            
            // Haptic feedback simulation
            function vibrate(pattern = [100]) {
                if ('vibrate' in navigator) {
                    navigator.vibrate(pattern);
                }
            }
            
            // Add haptic feedback to buttons
            const allButtons = document.querySelectorAll('button');
            allButtons.forEach(btn => {
                btn.addEventListener('click', function() {
                    vibrate([50]);
                });
            });
            
            // Auto-refresh data every 5 minutes
            setInterval(() => {
                console.log('Auto-refreshing dashboard data...');
                // In real implementation, fetch fresh data
            }, 300000);
            
            // Progressive Web App features
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/sw.js')
                    .then(registration => {
                        console.log('SW registered:', registration);
                    })
                    .catch(error => {
                        console.log('SW registration failed:', error);
                    });
            }
            
            // Offline detection
            window.addEventListener('online', function() {
                console.log('Back online');
                // Show online indicator
            });
            
            window.addEventListener('offline', function() {
                console.log('Gone offline');
                // Show offline indicator
            });
            
            // Battery status (if supported)
            if ('getBattery' in navigator) {
                navigator.getBattery().then(battery => {
                    console.log('Battery level:', battery.level * 100 + '%');
                    
                    if (battery.level < 0.2) {
                        console.log('Low battery - enabling power saving mode');
                        // Reduce refresh frequency, disable animations
                    }
                });
            }
            
            // Device orientation
            window.addEventListener('orientationchange', function() {
                console.log('Orientation changed');
                // Adjust layout if needed
            });
            
            // Touch-friendly interactions
            const touchTargets = document.querySelectorAll('button, .cursor-pointer');
            touchTargets.forEach(target => {
                // Ensure minimum 44px touch target
                const rect = target.getBoundingClientRect();
                if (rect.height < 44 || rect.width < 44) {
                    target.style.minHeight = '44px';
                    target.style.minWidth = '44px';
                }
            });
            
            // Keyboard shortcuts for accessibility
            document.addEventListener('keydown', function(e) {
                // Space or Enter to activate focused element
                if ((e.key === ' ' || e.key === 'Enter') && document.activeElement.tagName === 'BUTTON') {
                    e.preventDefault();
                    document.activeElement.click();
                }
                
                // Tab navigation enhancement
                if (e.key === 'Tab') {
                    document.body.classList.add('keyboard-navigation');
                }
            });
            
            // Remove keyboard navigation class on mouse use
            document.addEventListener('mousedown', function() {
                document.body.classList.remove('keyboard-navigation');
            });
            
            // Focus management for mobile
            const focusableElements = document.querySelectorAll('button, input, select, textarea, a[href]');
            focusableElements.forEach(element => {
                element.addEventListener('focus', function() {
                    this.scrollIntoView({ behavior: 'smooth', block: 'center' });
                });
            });
        });
    </script>
    
    <style>
        /* Custom styles for mobile optimization */
        .keyboard-navigation button:focus,
        .keyboard-navigation input:focus,
        .keyboard-navigation select:focus,
        .keyboard-navigation textarea:focus {
            outline: 2px solid #3b82f6;
            outline-offset: 2px;
        }
        
        /* Smooth scrolling */
        html {
            scroll-behavior: smooth;
        }
        
        /* Prevent zoom on input focus (iOS) */
        input, select, textarea {
            font-size: 16px;
        }
        
        /* Custom scrollbar for webkit browsers */
        ::-webkit-scrollbar {
            width: 4px;
        }
        
        ::-webkit-scrollbar-track {
            background: #f1f5f9;
        }
        
        ::-webkit-scrollbar-thumb {
            background: #cbd5e1;
            border-radius: 2px;
        }
        
        ::-webkit-scrollbar-thumb:hover {
            background: #94a3b8;
        }
        
        /* Safe area insets for devices with notches */
        @supports (padding: max(0px)) {
            .fixed.bottom-0 {
                padding-bottom: max(8px, env(safe-area-inset-bottom));
            }
            
            .sticky.top-0 {
                padding-top: max(0px, env(safe-area-inset-top));
            }
        }
        
        /* Dark mode support */
        @media (prefers-color-scheme: dark) {
            /* Dark mode styles would go here */
        }
        
        /* Reduced motion support */
        @media (prefers-reduced-motion: reduce) {
            * {
                animation-duration: 0.01ms !important;
                animation-iteration-count: 1 !important;
                transition-duration: 0.01ms !important;
            }
        }
        
        /* High contrast mode support */
        @media (prefers-contrast: high) {
            .border-gray-200 {
                border-color: #000;
            }
            
            .text-gray-600 {
                color: #000;
            }
        }
    </style>


    </div>
  );
};

export default Untitled1;