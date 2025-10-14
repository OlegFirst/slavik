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
                <div className="relative">
                    <input type="text" placeholder="Search community..." className="w-64 pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm" />
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
                        <a href="#" className="bg-primary-50 text-primary-700 group flex items-center px-2 py-2 text-sm font-medium rounded-md">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="graduation-cap" className="lucide lucide-graduation-cap text-primary-500 mr-3 h-5 w-5"><path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z"></path><path d="M22 10v6"></path><path d="M6 12.5V16a6 3 0 0 0 12 0v-3.5"></path></svg>
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
                    
                    <div className="mb-8">
                        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900">Community &amp; Learning</h1>
                                <p className="mt-1 text-sm text-gray-500">Connect with peers, learn best practices, and advance your BCM expertise</p>
                            </div>
                            <div className="mt-4 sm:mt-0 flex space-x-3">
                                <button className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="plus" className="lucide lucide-plus w-4 h-4 mr-2"><path d="M5 12h14"></path><path d="M12 5v14"></path></svg>
                                    New Discussion
                                </button>
                                <button className="bg-primary-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors flex items-center">
                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="users" className="lucide lucide-users w-4 h-4 mr-2"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path><path d="M16 3.128a4 4 0 0 1 0 7.744"></path><path d="M22 21v-2a4 4 0 0 0-3-3.87"></path><circle cx="9" cy="7" r="4"></circle></svg>
                                    Join Community
                                </button>
                            </div>
                        </div>
                    </div>

                    
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="users" className="lucide lucide-users w-5 h-5 text-blue-600"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path><path d="M16 3.128a4 4 0 0 1 0 7.744"></path><path d="M22 21v-2a4 4 0 0 0-3-3.87"></path><circle cx="9" cy="7" r="4"></circle></svg>
                                    </div>
                                </div>
                                <div className="ml-4">
                                    <p className="text-sm font-medium text-gray-500">Community Members</p>
                                    <p className="text-2xl font-bold text-gray-900">2,847</p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="book-open" className="lucide lucide-book-open w-5 h-5 text-green-600"><path d="M12 7v14"></path><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"></path></svg>
                                    </div>
                                </div>
                                <div className="ml-4">
                                    <p className="text-sm font-medium text-gray-500">Learning Modules</p>
                                    <p className="text-2xl font-bold text-gray-900">156</p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="file-text" className="lucide lucide-file-text w-5 h-5 text-purple-600"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"></path><path d="M14 2v4a2 2 0 0 0 2 2h4"></path><path d="M10 9H8"></path><path d="M16 13H8"></path><path d="M16 17H8"></path></svg>
                                    </div>
                                </div>
                                <div className="ml-4">
                                    <p className="text-sm font-medium text-gray-500">Case Studies</p>
                                    <p className="text-2xl font-bold text-gray-900">89</p>
                                </div>
                            </div>
                        </div>

                        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                            <div className="flex items-center">
                                <div className="flex-shrink-0">
                                    <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="award" className="lucide lucide-award w-5 h-5 text-orange-600"><path d="m15.477 12.89 1.515 8.526a.5.5 0 0 1-.81.47l-3.58-2.687a1 1 0 0 0-1.197 0l-3.586 2.686a.5.5 0 0 1-.81-.469l1.514-8.526"></path><circle cx="12" cy="8" r="6"></circle></svg>
                                    </div>
                                </div>
                                <div className="ml-4">
                                    <p className="text-sm font-medium text-gray-500">Certifications</p>
                                    <p className="text-2xl font-bold text-gray-900">12</p>
                                </div>
                            </div>
                        </div>
                    </div>

                    
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        
                        <div className="lg:col-span-2 space-y-6">
                            
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                                <div className="px-6 py-4 border-b border-gray-200">
                                    <div className="flex items-center justify-between">
                                        <h3 className="text-lg font-semibold text-gray-900">Recent Discussions</h3>
                                        <div className="flex space-x-2">
                                            <button className="text-sm text-gray-500 hover:text-gray-700 px-3 py-1 rounded-md hover:bg-gray-100 transition-colors">All</button>
                                            <button className="text-sm text-primary-600 bg-primary-50 px-3 py-1 rounded-md font-medium">Popular</button>
                                            <button className="text-sm text-gray-500 hover:text-gray-700 px-3 py-1 rounded-md hover:bg-gray-100 transition-colors">Unanswered</button>
                                        </div>
                                    </div>
                                </div>
                                <div className="divide-y divide-gray-200">
                                    <div className="p-6 hover:bg-gray-50 transition-colors cursor-pointer">
                                        <div className="flex items-start space-x-4">
                                            <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                                                <span className="text-sm font-medium text-blue-600">SM</span>
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-center space-x-2 mb-1">
                                                    <h4 className="text-sm font-medium text-gray-900 truncate">Best practices for RTO/RPO setting in financial services?</h4>
                                                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-orange-100 text-orange-800">Hot</span>
                                                </div>
                                                <p className="text-sm text-gray-600 line-clamp-2">We're struggling with setting appropriate RTO/RPO values for our critical financial processes. What are industry standards and how do you balance cost vs. availability?</p>
                                                <div className="flex items-center space-x-4 mt-3 text-xs text-gray-500">
                                                    <span>Sarah Miller • 2 hours ago</span>
                                                    <span className="flex items-center"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="message-circle" className="lucide lucide-message-circle w-3 h-3 mr-1"><path d="M2.992 16.342a2 2 0 0 1 .094 1.167l-1.065 3.29a1 1 0 0 0 1.236 1.168l3.413-.998a2 2 0 0 1 1.099.092 10 10 0 1 0-4.777-4.719"></path></svg>23 replies</span>
                                                    <span className="flex items-center"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="heart" className="lucide lucide-heart w-3 h-3 mr-1"><path d="M2 9.5a5.5 5.5 0 0 1 9.591-3.676.56.56 0 0 0 .818 0A5.49 5.49 0 0 1 22 9.5c0 2.29-1.5 4-3 5.5l-5.492 5.313a2 2 0 0 1-3 .019L5 15c-1.5-1.5-3-3.2-3-5.5"></path></svg>15 likes</span>
                                                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">Financial Services</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="p-6 hover:bg-gray-50 transition-colors cursor-pointer">
                                        <div className="flex items-start space-x-4">
                                            <div className="w-10 h-10 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                                                <span className="text-sm font-medium text-green-600">MJ</span>
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-center space-x-2 mb-1">
                                                    <h4 className="text-sm font-medium text-gray-900 truncate">ISO 22301:2019 vs 2012 - Key changes for compliance</h4>
                                                </div>
                                                <p className="text-sm text-gray-600 line-clamp-2">Can someone summarize the major changes between ISO 22301:2012 and 2019 versions? We're planning our compliance update and want to understand the impact.</p>
                                                <div className="flex items-center space-x-4 mt-3 text-xs text-gray-500">
                                                    <span>Michael Johnson • 4 hours ago</span>
                                                    <span className="flex items-center"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="message-circle" className="lucide lucide-message-circle w-3 h-3 mr-1"><path d="M2.992 16.342a2 2 0 0 1 .094 1.167l-1.065 3.29a1 1 0 0 0 1.236 1.168l3.413-.998a2 2 0 0 1 1.099.092 10 10 0 1 0-4.777-4.719"></path></svg>8 replies</span>
                                                    <span className="flex items-center"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="heart" className="lucide lucide-heart w-3 h-3 mr-1"><path d="M2 9.5a5.5 5.5 0 0 1 9.591-3.676.56.56 0 0 0 .818 0A5.49 5.49 0 0 1 22 9.5c0 2.29-1.5 4-3 5.5l-5.492 5.313a2 2 0 0 1-3 .019L5 15c-1.5-1.5-3-3.2-3-5.5"></path></svg>12 likes</span>
                                                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">ISO 22301</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="p-6 hover:bg-gray-50 transition-colors cursor-pointer">
                                        <div className="flex items-start space-x-4">
                                            <div className="w-10 h-10 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                                                <span className="text-sm font-medium text-purple-600">EB</span>
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-center space-x-2 mb-1">
                                                    <h4 className="text-sm font-medium text-gray-900 truncate">Cloud provider BCP - How to assess and integrate?</h4>
                                                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">Solved</span>
                                                </div>
                                                <p className="text-sm text-gray-600 line-clamp-2">We're moving to cloud infrastructure. How do you integrate cloud provider BCPs into your own continuity planning? What questions should we ask?</p>
                                                <div className="flex items-center space-x-4 mt-3 text-xs text-gray-500">
                                                    <span>Emily Brown • 6 hours ago</span>
                                                    <span className="flex items-center"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="message-circle" className="lucide lucide-message-circle w-3 h-3 mr-1"><path d="M2.992 16.342a2 2 0 0 1 .094 1.167l-1.065 3.29a1 1 0 0 0 1.236 1.168l3.413-.998a2 2 0 0 1 1.099.092 10 10 0 1 0-4.777-4.719"></path></svg>15 replies</span>
                                                    <span className="flex items-center"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="heart" className="lucide lucide-heart w-3 h-3 mr-1"><path d="M2 9.5a5.5 5.5 0 0 1 9.591-3.676.56.56 0 0 0 .818 0A5.49 5.49 0 0 1 22 9.5c0 2.29-1.5 4-3 5.5l-5.492 5.313a2 2 0 0 1-3 .019L5 15c-1.5-1.5-3-3.2-3-5.5"></path></svg>9 likes</span>
                                                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800">Cloud</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div className="p-6 hover:bg-gray-50 transition-colors cursor-pointer">
                                        <div className="flex items-start space-x-4">
                                            <div className="w-10 h-10 bg-orange-100 rounded-full flex items-center justify-center flex-shrink-0">
                                                <span className="text-sm font-medium text-orange-600">DW</span>
                                            </div>
                                            <div className="flex-1 min-w-0">
                                                <div className="flex items-center space-x-2 mb-1">
                                                    <h4 className="text-sm font-medium text-gray-900 truncate">Tabletop exercise scenarios - Share your favorites</h4>
                                                </div>
                                                <p className="text-sm text-gray-600 line-clamp-2">Looking for creative tabletop exercise scenarios. What scenarios have worked well for your organization? Especially interested in remote work challenges.</p>
                                                <div className="flex items-center space-x-4 mt-3 text-xs text-gray-500">
                                                    <span>David Wilson • 1 day ago</span>
                                                    <span className="flex items-center"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="message-circle" className="lucide lucide-message-circle w-3 h-3 mr-1"><path d="M2.992 16.342a2 2 0 0 1 .094 1.167l-1.065 3.29a1 1 0 0 0 1.236 1.168l3.413-.998a2 2 0 0 1 1.099.092 10 10 0 1 0-4.777-4.719"></path></svg>31 replies</span>
                                                    <span className="flex items-center"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="heart" className="lucide lucide-heart w-3 h-3 mr-1"><path d="M2 9.5a5.5 5.5 0 0 1 9.591-3.676.56.56 0 0 0 .818 0A5.49 5.49 0 0 1 22 9.5c0 2.29-1.5 4-3 5.5l-5.492 5.313a2 2 0 0 1-3 .019L5 15c-1.5-1.5-3-3.2-3-5.5"></path></svg>24 likes</span>
                                                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-orange-100 text-orange-800">Exercises</span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                <div className="px-6 py-4 border-t border-gray-200">
                                    <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">View All Discussions →</button>
                                </div>
                            </div>

                            
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                                <div className="px-6 py-4 border-b border-gray-200">
                                    <h3 className="text-lg font-semibold text-gray-900">Featured Case Studies</h3>
                                </div>
                                <div className="p-6">
                                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                        <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer">
                                            <div className="flex items-center space-x-2 mb-3">
                                                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800">Critical</span>
                                                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">Healthcare</span>
                                            </div>
                                            <h4 className="text-sm font-semibold text-gray-900 mb-2">Hospital System Ransomware Recovery</h4>
                                            <p className="text-xs text-gray-600 mb-3">How a 500-bed hospital system recovered from a major ransomware attack in 72 hours using their BCP.</p>
                                            <div className="flex items-center justify-between text-xs text-gray-500">
                                                <span>15 min read</span>
                                                <span className="flex items-center"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="eye" className="lucide lucide-eye w-3 h-3 mr-1"><path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"></path><circle cx="12" cy="12" r="3"></circle></svg>1.2k views</span>
                                            </div>
                                        </div>

                                        <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer">
                                            <div className="flex items-center space-x-2 mb-3">
                                                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-yellow-100 text-yellow-800">Lessons</span>
                                                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">Manufacturing</span>
                                            </div>
                                            <h4 className="text-sm font-semibold text-gray-900 mb-2">Supply Chain Disruption Management</h4>
                                            <p className="text-xs text-gray-600 mb-3">Automotive manufacturer's response to global supply chain disruptions during COVID-19.</p>
                                            <div className="flex items-center justify-between text-xs text-gray-500">
                                                <span>12 min read</span>
                                                <span className="flex items-center"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="eye" className="lucide lucide-eye w-3 h-3 mr-1"><path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"></path><circle cx="12" cy="12" r="3"></circle></svg>890 views</span>
                                            </div>
                                        </div>

                                        <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer">
                                            <div className="flex items-center space-x-2 mb-3">
                                                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">Success</span>
                                                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800">Financial</span>
                                            </div>
                                            <h4 className="text-sm font-semibold text-gray-900 mb-2">Bank Data Center Fire Recovery</h4>
                                            <p className="text-xs text-gray-600 mb-3">Regional bank's successful failover to backup data center within RTO targets.</p>
                                            <div className="flex items-center justify-between text-xs text-gray-500">
                                                <span>8 min read</span>
                                                <span className="flex items-center"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="eye" className="lucide lucide-eye w-3 h-3 mr-1"><path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"></path><circle cx="12" cy="12" r="3"></circle></svg>756 views</span>
                                            </div>
                                        </div>

                                        <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer">
                                            <div className="flex items-center space-x-2 mb-3">
                                                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">Innovation</span>
                                                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-orange-100 text-orange-800">Retail</span>
                                            </div>
                                            <h4 className="text-sm font-semibold text-gray-900 mb-2">E-commerce Platform Scaling</h4>
                                            <p className="text-xs text-gray-600 mb-3">How an online retailer handled 10x traffic surge during Black Friday using automated scaling.</p>
                                            <div className="flex items-center justify-between text-xs text-gray-500">
                                                <span>10 min read</span>
                                                <span className="flex items-center"><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="eye" className="lucide lucide-eye w-3 h-3 mr-1"><path d="M2.062 12.348a1 1 0 0 1 0-.696 10.75 10.75 0 0 1 19.876 0 1 1 0 0 1 0 .696 10.75 10.75 0 0 1-19.876 0"></path><circle cx="12" cy="12" r="3"></circle></svg>623 views</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        
                        <div className="space-y-6">
                            
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                                <div className="px-6 py-4 border-b border-gray-200">
                                    <h3 className="text-lg font-semibold text-gray-900">Your Learning Progress</h3>
                                </div>
                                <div className="p-6">
                                    <div className="text-center mb-6">
                                        <div className="relative w-24 h-24 mx-auto">
                                            <svg className="w-24 h-24 transform -rotate-90" viewBox="0 0 100 100">
                                                <circle cx="50" cy="50" r="40" stroke="#e5e7eb" stroke-width="8" fill="none"></circle>
                                                <circle cx="50" cy="50" r="40" stroke="#3b82f6" stroke-width="8" fill="none" stroke-dasharray="251.2" stroke-dashoffset="75.36" stroke-linecap="round"></circle>
                                            </svg>
                                            <div className="absolute inset-0 flex items-center justify-center">
                                                <span className="text-xl font-bold text-gray-900">70%</span>
                                            </div>
                                        </div>
                                        <p className="text-sm text-gray-600 mt-2">BCM Fundamentals</p>
                                    </div>
                                    
                                    <div className="space-y-4">
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center space-x-3">
                                                <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check" className="lucide lucide-check w-4 h-4 text-green-600"><path d="M20 6 9 17l-5-5"></path></svg>
                                                </div>
                                                <span className="text-sm text-gray-900">ISO 22301 Basics</span>
                                            </div>
                                            <span className="text-xs text-green-600 font-medium">Complete</span>
                                        </div>
                                        
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center space-x-3">
                                                <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check" className="lucide lucide-check w-4 h-4 text-green-600"><path d="M20 6 9 17l-5-5"></path></svg>
                                                </div>
                                                <span className="text-sm text-gray-900">BIA Fundamentals</span>
                                            </div>
                                            <span className="text-xs text-green-600 font-medium">Complete</span>
                                        </div>
                                        
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center space-x-3">
                                                <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="play" className="lucide lucide-play w-4 h-4 text-blue-600"><path d="M5 5a2 2 0 0 1 3.008-1.728l11.997 6.998a2 2 0 0 1 .003 3.458l-12 7A2 2 0 0 1 5 19z"></path></svg>
                                                </div>
                                                <span className="text-sm text-gray-900">Risk Assessment</span>
                                            </div>
                                            <span className="text-xs text-blue-600 font-medium">In Progress</span>
                                        </div>
                                        
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center space-x-3">
                                                <div className="w-8 h-8 bg-gray-100 rounded-lg flex items-center justify-center">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="lock" className="lucide lucide-lock w-4 h-4 text-gray-400"><rect width="18" height="11" x="3" y="11" rx="2" ry="2"></rect><path d="M7 11V7a5 5 0 0 1 10 0v4"></path></svg>
                                                </div>
                                                <span className="text-sm text-gray-500">Plan Development</span>
                                            </div>
                                            <span className="text-xs text-gray-400 font-medium">Locked</span>
                                        </div>
                                    </div>
                                    
                                    <button className="w-full mt-6 bg-primary-600 text-white py-2 px-4 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors">
                                        Continue Learning
                                    </button>
                                </div>
                            </div>

                            
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                                <div className="px-6 py-4 border-b border-gray-200">
                                    <h3 className="text-lg font-semibold text-gray-900">Recommended for You</h3>
                                </div>
                                <div className="p-6 space-y-4">
                                    <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer">
                                        <div className="flex items-center space-x-2 mb-2">
                                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">Course</span>
                                            <span className="text-xs text-gray-500">2h 30m</span>
                                        </div>
                                        <h4 className="text-sm font-semibold text-gray-900 mb-1">Advanced Risk Assessment Techniques</h4>
                                        <p className="text-xs text-gray-600 mb-2">Deep dive into quantitative risk analysis and modeling</p>
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center space-x-1">
                                                <div className="flex text-yellow-400">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="star" className="lucide lucide-star w-3 h-3 fill-current"><path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"></path></svg>
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="star" className="lucide lucide-star w-3 h-3 fill-current"><path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"></path></svg>
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="star" className="lucide lucide-star w-3 h-3 fill-current"><path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"></path></svg>
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="star" className="lucide lucide-star w-3 h-3 fill-current"><path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"></path></svg>
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="star" className="lucide lucide-star w-3 h-3"><path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"></path></svg>
                                                </div>
                                                <span className="text-xs text-gray-500">4.2</span>
                                            </div>
                                            <span className="text-xs text-gray-500">1,234 enrolled</span>
                                        </div>
                                    </div>

                                    <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer">
                                        <div className="flex items-center space-x-2 mb-2">
                                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">Webinar</span>
                                            <span className="text-xs text-gray-500">Live • Dec 15</span>
                                        </div>
                                        <h4 className="text-sm font-semibold text-gray-900 mb-1">Crisis Communication Best Practices</h4>
                                        <p className="text-xs text-gray-600 mb-2">Expert panel on effective crisis communication strategies</p>
                                        <div className="flex items-center justify-between">
                                            <span className="text-xs text-green-600 font-medium">Free</span>
                                            <span className="text-xs text-gray-500">245 registered</span>
                                        </div>
                                    </div>

                                    <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer">
                                        <div className="flex items-center space-x-2 mb-2">
                                            <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800">Certification</span>
                                            <span className="text-xs text-gray-500">8 weeks</span>
                                        </div>
                                        <h4 className="text-sm font-semibold text-gray-900 mb-1">Certified BCM Professional</h4>
                                        <p className="text-xs text-gray-600 mb-2">Comprehensive certification program with hands-on projects</p>
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center space-x-1">
                                                <div className="flex text-yellow-400">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="star" className="lucide lucide-star w-3 h-3 fill-current"><path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"></path></svg>
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="star" className="lucide lucide-star w-3 h-3 fill-current"><path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"></path></svg>
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="star" className="lucide lucide-star w-3 h-3 fill-current"><path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"></path></svg>
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="star" className="lucide lucide-star w-3 h-3 fill-current"><path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"></path></svg>
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="star" className="lucide lucide-star w-3 h-3 fill-current"><path d="M11.525 2.295a.53.53 0 0 1 .95 0l2.31 4.679a2.123 2.123 0 0 0 1.595 1.16l5.166.756a.53.53 0 0 1 .294.904l-3.736 3.638a2.123 2.123 0 0 0-.611 1.878l.882 5.14a.53.53 0 0 1-.771.56l-4.618-2.428a2.122 2.122 0 0 0-1.973 0L6.396 21.01a.53.53 0 0 1-.77-.56l.881-5.139a2.122 2.122 0 0 0-.611-1.879L2.16 9.795a.53.53 0 0 1 .294-.906l5.165-.755a2.122 2.122 0 0 0 1.597-1.16z"></path></svg>
                                                </div>
                                                <span className="text-xs text-gray-500">4.8</span>
                                            </div>
                                            <span className="text-xs text-gray-500">567 certified</span>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                                <div className="px-6 py-4 border-b border-gray-200">
                                    <h3 className="text-lg font-semibold text-gray-900">Community Highlights</h3>
                                </div>
                                <div className="p-6 space-y-4">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-8 h-8 bg-blue-100 rounded-lg flex items-center justify-center">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="trending-up" className="lucide lucide-trending-up w-4 h-4 text-blue-600"><path d="M16 7h6v6"></path><path d="m22 7-8.5 8.5-5-5L2 17"></path></svg>
                                        </div>
                                        <div>
                                            <p className="text-sm font-medium text-gray-900">Most Active Topic</p>
                                            <p className="text-xs text-gray-500">Remote Work BCM</p>
                                        </div>
                                    </div>
                                    
                                    <div className="flex items-center space-x-3">
                                        <div className="w-8 h-8 bg-green-100 rounded-lg flex items-center justify-center">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="users" className="lucide lucide-users w-4 h-4 text-green-600"><path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"></path><path d="M16 3.128a4 4 0 0 1 0 7.744"></path><path d="M22 21v-2a4 4 0 0 0-3-3.87"></path><circle cx="9" cy="7" r="4"></circle></svg>
                                        </div>
                                        <div>
                                            <p className="text-sm font-medium text-gray-900">New Members This Week</p>
                                            <p className="text-xs text-gray-500">47 professionals joined</p>
                                        </div>
                                    </div>
                                    
                                    <div className="flex items-center space-x-3">
                                        <div className="w-8 h-8 bg-purple-100 rounded-lg flex items-center justify-center">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="award" className="lucide lucide-award w-4 h-4 text-purple-600"><path d="m15.477 12.89 1.515 8.526a.5.5 0 0 1-.81.47l-3.58-2.687a1 1 0 0 0-1.197 0l-3.586 2.686a.5.5 0 0 1-.81-.469l1.514-8.526"></path><circle cx="12" cy="8" r="6"></circle></svg>
                                        </div>
                                        <div>
                                            <p className="text-sm font-medium text-gray-900">Top Contributor</p>
                                            <p className="text-xs text-gray-500">Dr. Amanda Chen</p>
                                        </div>
                                    </div>
                                    
                                    <div className="flex items-center space-x-3">
                                        <div className="w-8 h-8 bg-orange-100 rounded-lg flex items-center justify-center">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="calendar" className="lucide lucide-calendar w-4 h-4 text-orange-600"><path d="M8 2v4"></path><path d="M16 2v4"></path><rect width="18" height="18" x="3" y="4" rx="2"></rect><path d="M3 10h18"></path></svg>
                                        </div>
                                        <div>
                                            <p className="text-sm font-medium text-gray-900">Upcoming Event</p>
                                            <p className="text-xs text-gray-500">BCM Summit 2024</p>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                                <div className="px-6 py-4 border-b border-gray-200">
                                    <h3 className="text-lg font-semibold text-gray-900">Quick Actions</h3>
                                </div>
                                <div className="p-6 space-y-3">
                                    <button className="w-full text-left p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors flex items-center space-x-3">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="help-circle" className="lucide lucide-help-circle w-5 h-5 text-blue-600"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><path d="M12 17h.01"></path></svg>
                                        <span className="text-sm font-medium text-gray-900">Ask a Question</span>
                                    </button>
                                    
                                    <button className="w-full text-left p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors flex items-center space-x-3">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="share" className="lucide lucide-share w-5 h-5 text-green-600"><path d="M12 2v13"></path><path d="m16 6-4-4-4 4"></path><path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"></path></svg>
                                        <span className="text-sm font-medium text-gray-900">Share Experience</span>
                                    </button>
                                    
                                    <button className="w-full text-left p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors flex items-center space-x-3">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="book-open" className="lucide lucide-book-open w-5 h-5 text-purple-600"><path d="M12 7v14"></path><path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z"></path></svg>
                                        <span className="text-sm font-medium text-gray-900">Browse Library</span>
                                    </button>
                                    
                                    <button className="w-full text-left p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors flex items-center space-x-3">
                                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="calendar" className="lucide lucide-calendar w-5 h-5 text-orange-600"><path d="M8 2v4"></path><path d="M16 2v4"></path><rect width="18" height="18" x="3" y="4" rx="2"></rect><path d="M3 10h18"></path></svg>
                                        <span className="text-sm font-medium text-gray-900">Join Event</span>
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
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="layout-dashboard" className="lucide lucide-layout-dashboard w-5 h-5"><rect width="7" height="9" x="3" y="3" rx="1"></rect><rect width="7" height="5" x="14" y="3" rx="1"></rect><rect width="7" height="9" x="14" y="12" rx="1"></rect><rect width="7" height="5" x="3" y="16" rx="1"></rect></svg>
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
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="graduation-cap" className="lucide lucide-graduation-cap w-5 h-5"><path d="M21.42 10.922a1 1 0 0 0-.019-1.838L12.83 5.18a2 2 0 0 0-1.66 0L2.6 9.08a1 1 0 0 0 0 1.832l8.57 3.908a2 2 0 0 0 1.66 0z"></path><path d="M22 10v6"></path><path d="M6 12.5V16a6 3 0 0 0 12 0v-3.5"></path></svg>
                <span className="text-xs mt-1 font-medium">Learning</span>
            </button>
        </div>
    </div>

    <script>
        // Initialize Lucide icons
        lucide.createIcons();
        
        document.addEventListener('DOMContentLoaded', function() {
            // Discussion interaction
            const discussionItems = document.querySelectorAll('.divide-y > div');
            discussionItems.forEach(item => {
                item.addEventListener('click', function() {
                    console.log('Opening discussion...');
                    // In real implementation, navigate to discussion detail
                });
            });
            
            // Case study interaction
            const caseStudyCards = document.querySelectorAll('.grid .border.border-gray-200');
            caseStudyCards.forEach(card => {
                card.addEventListener('click', function() {
                    console.log('Opening case study...');
                    // In real implementation, open case study detail
                });
            });
            
            // Course interaction
            const courseCards = document.querySelectorAll('.space-y-4 .border.border-gray-200');
            courseCards.forEach(card => {
                card.addEventListener('click', function() {
                    console.log('Opening course...');
                    // In real implementation, navigate to course
                });
            });
            
            // New Discussion button
            const newDiscussionBtn = document.querySelector('button:has(i[data-lucide="plus"])');
            if (newDiscussionBtn) {
                newDiscussionBtn.addEventListener('click', function() {
                    console.log('Opening new discussion form...');
                    // In real implementation, show discussion creation modal
                });
            }
            
            // Join Community button
            const joinCommunityBtn = document.querySelector('button:has(i[data-lucide="users"])');
            if (joinCommunityBtn) {
                joinCommunityBtn.addEventListener('click', function() {
                    console.log('Joining community...');
                    // In real implementation, handle community join
                });
            }
            
            // Continue Learning button
            const continueLearningBtn = document.querySelector('button:contains("Continue Learning")');
            document.querySelectorAll('button').forEach(button => {
                if (button.textContent.includes('Continue Learning')) {
                    button.addEventListener('click', function() {
                        console.log('Continuing learning path...');
                        // In real implementation, navigate to next lesson
                    });
                }
            });
            
            // Discussion filter buttons
            const filterButtons = document.querySelectorAll('.flex.space-x-2 button');
            filterButtons.forEach(button => {
                button.addEventListener('click', function() {
                    // Remove active state from all buttons
                    filterButtons.forEach(btn => {
                        btn.classList.remove('text-primary-600', 'bg-primary-50', 'font-medium');
                        btn.classList.add('text-gray-500');
                    });
                    
                    // Add active state to clicked button
                    this.classList.remove('text-gray-500');
                    this.classList.add('text-primary-600', 'bg-primary-50', 'font-medium');
                    
                    console.log(`Filtering discussions by: ${this.textContent}`);
                    // In real implementation, filter discussions
                });
            });
            
            // Quick action buttons
            const quickActionButtons = document.querySelectorAll('.space-y-3 button');
            quickActionButtons.forEach(button => {
                button.addEventListener('click', function() {
                    const action = this.querySelector('span').textContent;
                    console.log(`Quick action: ${action}`);
                    
                    switch(action) {
                        case 'Ask a Question':
                            // Show question form
                            break;
                        case 'Share Experience':
                            // Show experience sharing form
                            break;
                        case 'Browse Library':
                            // Navigate to library
                            break;
                        case 'Join Event':
                            // Show upcoming events
                            break;
                    }
                });
            });
            
            // Search functionality
            const searchInput = document.querySelector('input[placeholder="Search community..."]');
            if (searchInput) {
                searchInput.addEventListener('input', function() {
                    const query = this.value;
                    console.log(`Searching community for: ${query}`);
                    // In real implementation, perform search
                });
                
                searchInput.addEventListener('keypress', function(e) {
                    if (e.key === 'Enter') {
                        console.log('Performing search...');
                        // In real implementation, execute search
                    }
                });
            }
            
            // Like/heart functionality
            const heartIcons = document.querySelectorAll('i[data-lucide="heart"]');
            heartIcons.forEach(icon => {
                icon.parentElement.addEventListener('click', function(e) {
                    e.stopPropagation();
                    console.log('Toggling like...');
                    // In real implementation, toggle like status
                });
            });
            
            // Reply functionality
            const replyIcons = document.querySelectorAll('i[data-lucide="message-circle"]');
            replyIcons.forEach(icon => {
                icon.parentElement.addEventListener('click', function(e) {
                    e.stopPropagation();
                    console.log('Opening replies...');
                    // In real implementation, show replies
                });
            });
            
            // Learning progress animation
            const progressCircle = document.querySelector('circle[stroke="#3b82f6"]');
            if (progressCircle) {
                // Animate progress circle on load
                setTimeout(() => {
                    progressCircle.style.transition = 'stroke-dashoffset 2s ease-in-out';
                }, 500);
            }
            
            // Star rating interaction
            const starContainers = document.querySelectorAll('.flex.text-yellow-400');
            starContainers.forEach(container => {
                const stars = container.querySelectorAll('i[data-lucide="star"]');
                stars.forEach((star, index) => {
                    star.addEventListener('mouseenter', function() {
                        // Highlight stars up to current one
                        for (let i = 0; i <= index; i++) {
                            stars[i].classList.add('text-yellow-500');
                        }
                    });
                    
                    star.addEventListener('mouseleave', function() {
                        // Reset star colors
                        stars.forEach(s => s.classList.remove('text-yellow-500'));
                    });
                    
                    star.addEventListener('click', function() {
                        console.log(`Rated ${index + 1} stars`);
                        // In real implementation, submit rating
                    });
                });
            });
            
            // Keyboard shortcuts
            document.addEventListener('keydown', function(e) {
                // Ctrl/Cmd + K to focus search
                if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                    e.preventDefault();
                    searchInput?.focus();
                }
                
                // N to create new discussion
                if (e.key === 'n' && !e.ctrlKey && !e.metaKey && document.activeElement.tagName !== 'INPUT') {
                    newDiscussionBtn?.click();
                }
            });
            
            // Auto-refresh community stats
            setInterval(() => {
                console.log('Refreshing community stats...');
                // In real implementation, update stats via WebSocket or API
            }, 30000); // Every 30 seconds
            
            // Notification for new discussions
            function showNewDiscussionNotification() {
                // In real implementation, show toast notification
                console.log('New discussion available!');
            }
            
            // Simulate new discussion notification
            setTimeout(showNewDiscussionNotification, 10000);
        });
    </script>


    </div>
  );
};

export default Untitled1;