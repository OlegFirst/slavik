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
        
        <main className="flex-1 overflow-y-auto">
            <div className="py-6">
                <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
                    
                    <div className="mb-8">
                        <nav className="flex mb-3" aria-label="Breadcrumb">
                            <ol className="flex items-center space-x-2 text-sm text-gray-500">
                                <li><a href="#" className="hover:text-gray-700">Dashboard</a></li>
                                <li><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="chevron-right" className="lucide lucide-chevron-right w-4 h-4"><path d="m9 18 6-6-6-6"></path></svg></li>
                                <li><a href="#" className="hover:text-gray-700">Business Impact Analysis</a></li>
                                <li><svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="chevron-right" className="lucide lucide-chevron-right w-4 h-4"><path d="m9 18 6-6-6-6"></path></svg></li>
                                <li className="text-gray-900 font-medium">Create New BIA</li>
                            </ol>
                        </nav>
                        <div className="flex items-center justify-between">
                            <div>
                                <h1 className="text-2xl font-bold text-gray-900">Create New Business Impact Analysis</h1>
                                <p className="mt-1 text-sm text-gray-500">Step 1 of 6: Planning &amp; Setup</p>
                            </div>
                            <button className="bg-white border border-gray-300 text-gray-700 px-4 py-2 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors flex items-center">
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="save" className="lucide lucide-save w-4 h-4 mr-2"><path d="M15.2 3a2 2 0 0 1 1.4.6l3.8 3.8a2 2 0 0 1 .6 1.4V19a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2z"></path><path d="M17 21v-7a1 1 0 0 0-1-1H8a1 1 0 0 0-1 1v7"></path><path d="M7 3v4a1 1 0 0 0 1 1h7"></path></svg>
                                Save Draft
                            </button>
                        </div>
                    </div>

                    
                    <div className="mb-8">
                        <div className="flex items-center justify-between mb-4">
                            <div className="flex items-center space-x-4">
                                <div className="flex items-center">
                                    <div className="w-8 h-8 bg-primary-600 text-white rounded-full flex items-center justify-center text-sm font-medium">
                                        1
                                    </div>
                                    <span className="ml-3 text-sm font-medium text-primary-600">Planning</span>
                                </div>
                                <div className="w-16 h-1 bg-gray-200 rounded"></div>
                                <div className="flex items-center">
                                    <div className="w-8 h-8 bg-gray-200 text-gray-500 rounded-full flex items-center justify-center text-sm font-medium">
                                        2
                                    </div>
                                    <span className="ml-3 text-sm text-gray-500">Process Selection</span>
                                </div>
                                <div className="w-16 h-1 bg-gray-200 rounded"></div>
                                <div className="flex items-center">
                                    <div className="w-8 h-8 bg-gray-200 text-gray-500 rounded-full flex items-center justify-center text-sm font-medium">
                                        3
                                    </div>
                                    <span className="ml-3 text-sm text-gray-500">Data Collection</span>
                                </div>
                                <div className="hidden lg:flex items-center">
                                    <div className="w-16 h-1 bg-gray-200 rounded"></div>
                                    <div className="flex items-center">
                                        <div className="w-8 h-8 bg-gray-200 text-gray-500 rounded-full flex items-center justify-center text-sm font-medium">
                                            4
                                        </div>
                                        <span className="ml-3 text-sm text-gray-500">Dependencies</span>
                                    </div>
                                    <div className="w-16 h-1 bg-gray-200 rounded"></div>
                                    <div className="flex items-center">
                                        <div className="w-8 h-8 bg-gray-200 text-gray-500 rounded-full flex items-center justify-center text-sm font-medium">
                                            5
                                        </div>
                                        <span className="ml-3 text-sm text-gray-500">Impact Analysis</span>
                                    </div>
                                    <div className="w-16 h-1 bg-gray-200 rounded"></div>
                                    <div className="flex items-center">
                                        <div className="w-8 h-8 bg-gray-200 text-gray-500 rounded-full flex items-center justify-center text-sm font-medium">
                                            6
                                        </div>
                                        <span className="ml-3 text-sm text-gray-500">Review</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                            <div className="bg-primary-600 h-2 rounded-full" style={{width: '16.67%'}}></div>
                        </div>
                    </div>

                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                        
                        <div className="lg:col-span-2">
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200">
                                <div className="p-6">
                                    <div className="flex items-center justify-between mb-6">
                                        <h2 className="text-lg font-semibold text-gray-900">BIA Planning &amp; Setup</h2>
                                        <div className="flex items-center space-x-2 text-sm text-gray-500">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="clock" className="lucide lucide-clock w-4 h-4"><path d="M12 6v6l4 2"></path><circle cx="12" cy="12" r="10"></circle></svg>
                                            <span>Est. 5-10 minutes</span>
                                        </div>
                                    </div>

                                    <form className="space-y-6">
                                        
                                        <div>
                                            <label htmlFor="bia-name" className="block text-sm font-medium text-gray-700 mb-2">
                                                BIA Name *
                                            </label>
                                            <input type="text" id="bia-name" name="bia-name" className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500" placeholder="e.g., IT Infrastructure BIA Q4 2024" />
                                            <p className="mt-1 text-sm text-gray-500">Choose a descriptive name that clearly identifies this BIA</p>
                                        </div>

                                        
                                        <div>
                                            <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-2">
                                                Description
                                            </label>
                                            <textarea id="description" name="description" rows="3" className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500" placeholder="Describe the scope and objectives of this BIA..."></textarea>
                                        </div>

                                        
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-3">
                                                Analysis Scope *
                                            </label>
                                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                <label className="relative flex items-start p-4 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
                                                    <input type="radio" name="scope" value="department" className="mt-1 h-4 w-4 text-primary-600 border-gray-300 focus:ring-primary-500" />
                                                    <div className="ml-3">
                                                        <div className="text-sm font-medium text-gray-900">Department Level</div>
                                                        <div className="text-sm text-gray-500">Focus on specific department processes</div>
                                                    </div>
                                                </label>
                                                <label className="relative flex items-start p-4 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
                                                    <input type="radio" name="scope" value="organization" className="mt-1 h-4 w-4 text-primary-600 border-gray-300 focus:ring-primary-500" />
                                                    <div className="ml-3">
                                                        <div className="text-sm font-medium text-gray-900">Organization Wide</div>
                                                        <div className="text-sm text-gray-500">Comprehensive analysis across all departments</div>
                                                    </div>
                                                </label>
                                                <label className="relative flex items-start p-4 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
                                                    <input type="radio" name="scope" value="process" className="mt-1 h-4 w-4 text-primary-600 border-gray-300 focus:ring-primary-500" />
                                                    <div className="ml-3">
                                                        <div className="text-sm font-medium text-gray-900">Process Specific</div>
                                                        <div className="text-sm text-gray-500">Target specific business processes</div>
                                                    </div>
                                                </label>
                                                <label className="relative flex items-start p-4 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
                                                    <input type="radio" name="scope" value="system" className="mt-1 h-4 w-4 text-primary-600 border-gray-300 focus:ring-primary-500" />
                                                    <div className="ml-3">
                                                        <div className="text-sm font-medium text-gray-900">System/Technology</div>
                                                        <div className="text-sm text-gray-500">Focus on IT systems and technology</div>
                                                    </div>
                                                </label>
                                            </div>
                                        </div>

                                        
                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                            <div>
                                                <label htmlFor="start-date" className="block text-sm font-medium text-gray-700 mb-2">
                                                    Start Date *
                                                </label>
                                                <input type="date" id="start-date" name="start-date" className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500" />
                                            </div>
                                            <div>
                                                <label htmlFor="target-completion" className="block text-sm font-medium text-gray-700 mb-2">
                                                    Target Completion *
                                                </label>
                                                <input type="date" id="target-completion" name="target-completion" className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500" />
                                            </div>
                                        </div>

                                        
                                        <div>
                                            <label htmlFor="priority" className="block text-sm font-medium text-gray-700 mb-2">
                                                Priority Level *
                                            </label>
                                            <select id="priority" name="priority" className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500">
                                                <option value="">Select priority level</option>
                                                <option value="critical">Critical - Immediate attention required</option>
                                                <option value="high">High - Important for business continuity</option>
                                                <option value="medium">Medium - Standard business process</option>
                                                <option value="low">Low - Supporting process</option>
                                            </select>
                                        </div>

                                        
                                        <div>
                                            <label className="block text-sm font-medium text-gray-700 mb-3">
                                                BIA Team Members
                                            </label>
                                            <div className="space-y-3">
                                                <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                                                    <div className="flex items-center space-x-3">
                                                        <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                                                            <span className="text-sm font-medium text-primary-600">AJ</span>
                                                        </div>
                                                        <div>
                                                            <p className="text-sm font-medium text-gray-900">Alex Johnson</p>
                                                            <p className="text-xs text-gray-500">BIA Lead</p>
                                                        </div>
                                                    </div>
                                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                                                        Lead
                                                    </span>
                                                </div>
                                                <button type="button" className="w-full p-3 border-2 border-dashed border-gray-300 rounded-lg text-sm text-gray-500 hover:border-gray-400 hover:text-gray-600 transition-colors flex items-center justify-center">
                                                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="plus" className="lucide lucide-plus w-4 h-4 mr-2"><path d="M5 12h14"></path><path d="M12 5v14"></path></svg>
                                                    Add Team Member
                                                </button>
                                            </div>
                                        </div>

                                        
                                        <div>
                                            <label htmlFor="budget" className="block text-sm font-medium text-gray-700 mb-2">
                                                Estimated Budget (Optional)
                                            </label>
                                            <div className="relative">
                                                <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500">$</span>
                                                <input type="number" id="budget" name="budget" className="w-full pl-8 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500" placeholder="0.00" />
                                            </div>
                                            <p className="mt-1 text-sm text-gray-500">Include costs for resources, tools, and external consultants</p>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>

                        
                        <div className="lg:col-span-1">
                            <div className="bg-white rounded-lg shadow-sm border border-gray-200 sticky top-6">
                                <div className="p-4 border-b border-gray-200">
                                    <div className="flex items-center space-x-3">
                                        <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center">
                                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="bot" className="lucide lucide-bot w-4 h-4 text-primary-600"><path d="M12 8V4H8"></path><rect width="16" height="12" x="4" y="8" rx="2"></rect><path d="M2 14h2"></path><path d="M20 14h2"></path><path d="M15 13v2"></path><path d="M9 13v2"></path></svg>
                                        </div>
                                        <div>
                                            <h3 className="text-sm font-semibold text-gray-900">AI Assistant</h3>
                                            <p className="text-xs text-gray-500">BIA Planning Help</p>
                                        </div>
                                    </div>
                                </div>
                                
                                <div className="p-4">
                                    
                                    <div className="mb-6">
                                        <h4 className="text-sm font-medium text-gray-900 mb-3"> Smart Recommendations</h4>
                                        <div className="space-y-3">
                                            <div className="p-3 bg-primary-50 rounded-lg border border-primary-200">
                                                <p className="text-sm text-primary-800 mb-2"> Optimal Duration</p>
                                                <p className="text-xs text-primary-700">Based on your scope, I recommend 4-6 weeks for completion.</p>
                                            </div>
                                            <div className="p-3 bg-warning-50 rounded-lg border border-warning-200">
                                                <p className="text-sm text-warning-800 mb-2"> Team Size</p>
                                                <p className="text-xs text-warning-700">Consider adding 2-3 subject matter experts from key departments.</p>
                                            </div>
                                            <div className="p-3 bg-success-50 rounded-lg border border-success-200">
                                                <p className="text-sm text-success-800 mb-2"> Budget Estimate</p>
                                                <p className="text-xs text-success-700">Similar BIAs typically cost $15,000-25,000 including resources.</p>
                                            </div>
                                        </div>
                                    </div>

                                    
                                    <div className="mb-6">
                                        <h4 className="text-sm font-medium text-gray-900 mb-3"> Planning Tips</h4>
                                        <ul className="space-y-2 text-xs text-gray-600">
                                            <li className="flex items-start space-x-2">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check" className="lucide lucide-check w-3 h-3 text-success-500 mt-0.5 flex-shrink-0"><path d="M20 6 9 17l-5-5"></path></svg>
                                                <span>Start with critical processes first</span>
                                            </li>
                                            <li className="flex items-start space-x-2">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check" className="lucide lucide-check w-3 h-3 text-success-500 mt-0.5 flex-shrink-0"><path d="M20 6 9 17l-5-5"></path></svg>
                                                <span>Involve process owners early</span>
                                            </li>
                                            <li className="flex items-start space-x-2">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check" className="lucide lucide-check w-3 h-3 text-success-500 mt-0.5 flex-shrink-0"><path d="M20 6 9 17l-5-5"></path></svg>
                                                <span>Set realistic timelines</span>
                                            </li>
                                            <li className="flex items-start space-x-2">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="check" className="lucide lucide-check w-3 h-3 text-success-500 mt-0.5 flex-shrink-0"><path d="M20 6 9 17l-5-5"></path></svg>
                                                <span>Document assumptions clearly</span>
                                            </li>
                                        </ul>
                                    </div>

                                    
                                    <div>
                                        <h4 className="text-sm font-medium text-gray-900 mb-3"> Ask AI</h4>
                                        <div className="space-y-2 mb-3 max-h-32 overflow-y-auto">
                                            <div className="p-2 bg-gray-100 rounded text-xs text-gray-700">
                                                <strong>AI:</strong> I'm here to help with your BIA planning. What questions do you have?
                                            </div>
                                        </div>
                                        <div className="flex space-x-2">
                                            <input type="text" placeholder="Ask about BIA planning..." className="flex-1 px-3 py-2 text-xs border border-gray-300 rounded-lg focus:outline-none focus:ring-1 focus:ring-primary-500" />
                                            <button className="px-3 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors opacity-50 cursor-not-allowed" disabled="">
                                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="send" className="lucide lucide-send w-3 h-3"><path d="M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z"></path><path d="m21.854 2.147-10.94 10.939"></path></svg>
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    
                    <div className="mt-8 flex items-center justify-between">
                        <button className="bg-white border border-gray-300 text-gray-700 px-6 py-3 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors flex items-center">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="arrow-left" className="lucide lucide-arrow-left w-4 h-4 mr-2"><path d="m12 19-7-7 7-7"></path><path d="M19 12H5"></path></svg>
                            Back to BIA List
                        </button>
                        <div className="flex items-center space-x-3">
                            <button className="bg-white border border-gray-300 text-gray-700 px-6 py-3 rounded-lg text-sm font-medium hover:bg-gray-50 transition-colors">
                                Save Draft
                            </button>
                            <button className="bg-primary-600 text-white px-6 py-3 rounded-lg text-sm font-medium hover:bg-primary-700 transition-colors flex items-center">
                                Next: Process Selection
                                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="arrow-right" className="lucide lucide-arrow-right w-4 h-4 ml-2"><path d="M5 12h14"></path><path d="m12 5 7 7-7 7"></path></svg>
                            </button>
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
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-lucide="menu" className="lucide lucide-menu w-5 h-5"><path d="M4 5h16"></path><path d="M4 12h16"></path><path d="M4 19h16"></path></svg>
                <span className="text-xs mt-1">More</span>
            </button>
        </div>
    </div>

    <script>
        // Initialize Lucide icons
        lucide.createIcons();
        
        // Form validation and interactivity
        document.addEventListener('DOMContentLoaded', function() {
            // Auto-fill target completion date based on start date
            const startDateInput = document.getElementById('start-date');
            const targetCompletionInput = document.getElementById('target-completion');
            
            startDateInput.addEventListener('change', function() {
                if (this.value) {
                    const startDate = new Date(this.value);
                    const targetDate = new Date(startDate);
                    targetDate.setDate(startDate.getDate() + 42); // 6 weeks
                    targetCompletionInput.value = targetDate.toISOString().split('T')[0];
                }
            });
            
            // Form validation
            const form = document.querySelector('form');
            const requiredFields = form.querySelectorAll('[required], input[name="scope"]:checked');
            
            function validateForm() {
                const biaName = document.getElementById('bia-name').value;
                const scope = document.querySelector('input[name="scope"]:checked');
                const startDate = document.getElementById('start-date').value;
                const targetCompletion = document.getElementById('target-completion').value;
                const priority = document.getElementById('priority').value;
                
                const isValid = biaName && scope && startDate && targetCompletion && priority;
                
                const nextButton = document.querySelector('button[class*="bg-primary-600"]');
                if (nextButton) {
                    nextButton.disabled = !isValid;
                    nextButton.classList.toggle('opacity-50', !isValid);
                    nextButton.classList.toggle('cursor-not-allowed', !isValid);
                }
            }
            
            // Add event listeners for validation
            document.getElementById('bia-name').addEventListener('input', validateForm);
            document.querySelectorAll('input[name="scope"]').forEach(radio => {
                radio.addEventListener('change', validateForm);
            });
            document.getElementById('start-date').addEventListener('change', validateForm);
            document.getElementById('target-completion').addEventListener('change', validateForm);
            document.getElementById('priority').addEventListener('change', validateForm);
            
            // Initial validation
            validateForm();
            
            // AI Chat functionality
            const chatInput = document.querySelector('input[placeholder="Ask about BIA planning..."]');
            const chatButton = chatInput.nextElementSibling;
            
            function sendMessage() {
                const message = chatInput.value.trim();
                if (message) {
                    // Add user message to chat
                    const chatContainer = document.querySelector('.max-h-32.overflow-y-auto');
                    const userMessage = document.createElement('div');
                    userMessage.className = 'p-2 bg-primary-100 rounded text-xs text-primary-700 ml-4';
                    userMessage.innerHTML = `<strong>You:</strong> ${message}`;
                    chatContainer.appendChild(userMessage);
                    
                    // Simulate AI response
                    setTimeout(() => {
                        const aiResponse = document.createElement('div');
                        aiResponse.className = 'p-2 bg-gray-100 rounded text-xs text-gray-700';
                        aiResponse.innerHTML = `<strong>AI:</strong> That's a great question! Based on best practices, I recommend...`;
                        chatContainer.appendChild(aiResponse);
                        chatContainer.scrollTop = chatContainer.scrollHeight;
                    }, 1000);
                    
                    chatInput.value = '';
                    chatContainer.scrollTop = chatContainer.scrollHeight;
                }
            }
            
            chatButton.addEventListener('click', sendMessage);
            chatInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
        });
    </script>


    </div>
  );
};

export default Untitled1;