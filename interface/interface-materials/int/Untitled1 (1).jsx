import React from 'react';

const Untitled1 = () => {
  return (
    <div>
      
    
    <header className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
                <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center">
                        <i data-lucide="palette" className="w-6 h-6 text-white"></i>
                    </div>
                    <div>
                        <h1 className="text-xl font-bold text-gray-900 dark:text-white">AI-Platform-ISO</h1>
                        <p className="text-sm text-gray-500 dark:text-gray-400">Design System v2.0.0</p>
                    </div>
                </div>
                
                <div className="flex items-center space-x-4">
                    
                    <button id="themeToggle" className="p-2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
                        <i data-lucide="sun" className="w-5 h-5 dark:hidden"></i>
                        <i data-lucide="moon" className="w-5 h-5 hidden dark:block"></i>
                    </button>
                    
                    
                    <button id="langToggle" className="px-3 py-1 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
                        EN
                    </button>
                </div>
            </div>
        </div>
    </header>

    
    <nav className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex space-x-8 overflow-x-auto">
                <button className="nav-tab active py-4 px-1 border-b-2 border-primary-500 text-primary-600 dark:text-primary-400 font-medium text-sm whitespace-nowrap" data-tab="colors">
                    Colors
                </button>
                <button className="nav-tab py-4 px-1 border-b-2 border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 font-medium text-sm whitespace-nowrap" data-tab="typography">
                    Typography
                </button>
                <button className="nav-tab py-4 px-1 border-b-2 border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 font-medium text-sm whitespace-nowrap" data-tab="spacing">
                    Spacing
                </button>
                <button className="nav-tab py-4 px-1 border-b-2 border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 font-medium text-sm whitespace-nowrap" data-tab="buttons">
                    Buttons
                </button>
                <button className="nav-tab py-4 px-1 border-b-2 border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 font-medium text-sm whitespace-nowrap" data-tab="forms">
                    Forms
                </button>
                <button className="nav-tab py-4 px-1 border-b-2 border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 font-medium text-sm whitespace-nowrap" data-tab="cards">
                    Cards
                </button>
                <button className="nav-tab py-4 px-1 border-b-2 border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 font-medium text-sm whitespace-nowrap" data-tab="modals">
                    Modals
                </button>
                <button className="nav-tab py-4 px-1 border-b-2 border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 font-medium text-sm whitespace-nowrap" data-tab="icons">
                    Icons
                </button>
                <button className="nav-tab py-4 px-1 border-b-2 border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 font-medium text-sm whitespace-nowrap" data-tab="animations">
                    Animations
                </button>
            </div>
        </div>
    </nav>

    
    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        
        <div id="colors" className="tab-content">
            <div className="mb-8">
                <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Color Palette</h2>
                <p className="text-gray-600 dark:text-gray-400 mb-8">Our color system is designed to be accessible, consistent, and meaningful across all interfaces.</p>
            </div>

            
            <div className="mb-12">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Primary Colors</h3>
                <div className="grid grid-cols-2 md:grid-cols-5 lg:grid-cols-10 gap-4">
                    <div className="color-swatch" data-color="primary-50">
                        <div className="w-full h-20 bg-primary-50 rounded-lg border border-gray-200 dark:border-gray-600"></div>
                        <p className="text-xs font-mono mt-2 text-gray-600 dark:text-gray-400">50</p>
                        <p className="text-xs font-mono text-gray-500 dark:text-gray-500">#eff6ff</p>
                    </div>
                    <div className="color-swatch" data-color="primary-100">
                        <div className="w-full h-20 bg-primary-100 rounded-lg border border-gray-200 dark:border-gray-600"></div>
                        <p className="text-xs font-mono mt-2 text-gray-600 dark:text-gray-400">100</p>
                        <p className="text-xs font-mono text-gray-500 dark:text-gray-500">#dbeafe</p>
                    </div>
                    <div className="color-swatch" data-color="primary-200">
                        <div className="w-full h-20 bg-primary-200 rounded-lg border border-gray-200 dark:border-gray-600"></div>
                        <p className="text-xs font-mono mt-2 text-gray-600 dark:text-gray-400">200</p>
                        <p className="text-xs font-mono text-gray-500 dark:text-gray-500">#bfdbfe</p>
                    </div>
                    <div className="color-swatch" data-color="primary-300">
                        <div className="w-full h-20 bg-primary-300 rounded-lg border border-gray-200 dark:border-gray-600"></div>
                        <p className="text-xs font-mono mt-2 text-gray-600 dark:text-gray-400">300</p>
                        <p className="text-xs font-mono text-gray-500 dark:text-gray-500">#93c5fd</p>
                    </div>
                    <div className="color-swatch" data-color="primary-400">
                        <div className="w-full h-20 bg-primary-400 rounded-lg border border-gray-200 dark:border-gray-600"></div>
                        <p className="text-xs font-mono mt-2 text-gray-600 dark:text-gray-400">400</p>
                        <p className="text-xs font-mono text-gray-500 dark:text-gray-500">#60a5fa</p>
                    </div>
                    <div className="color-swatch" data-color="primary-500">
                        <div className="w-full h-20 bg-primary-500 rounded-lg border border-gray-200 dark:border-gray-600"></div>
                        <p className="text-xs font-mono mt-2 text-gray-600 dark:text-gray-400">500</p>
                        <p className="text-xs font-mono text-gray-500 dark:text-gray-500">#3b82f6</p>
                    </div>
                    <div className="color-swatch" data-color="primary-600">
                        <div className="w-full h-20 bg-primary-600 rounded-lg border border-gray-200 dark:border-gray-600"></div>
                        <p className="text-xs font-mono mt-2 text-gray-600 dark:text-gray-400">600</p>
                        <p className="text-xs font-mono text-gray-500 dark:text-gray-500">#2563eb</p>
                    </div>
                    <div className="color-swatch" data-color="primary-700">
                        <div className="w-full h-20 bg-primary-700 rounded-lg border border-gray-200 dark:border-gray-600"></div>
                        <p className="text-xs font-mono mt-2 text-gray-600 dark:text-gray-400">700</p>
                        <p className="text-xs font-mono text-gray-500 dark:text-gray-500">#1d4ed8</p>
                    </div>
                    <div className="color-swatch" data-color="primary-800">
                        <div className="w-full h-20 bg-primary-800 rounded-lg border border-gray-200 dark:border-gray-600"></div>
                        <p className="text-xs font-mono mt-2 text-gray-600 dark:text-gray-400">800</p>
                        <p className="text-xs font-mono text-gray-500 dark:text-gray-500">#1e40af</p>
                    </div>
                    <div className="color-swatch" data-color="primary-900">
                        <div className="w-full h-20 bg-primary-900 rounded-lg border border-gray-200 dark:border-gray-600"></div>
                        <p className="text-xs font-mono mt-2 text-gray-600 dark:text-gray-400">900</p>
                        <p className="text-xs font-mono text-gray-500 dark:text-gray-500">#1e3a8a</p>
                    </div>
                </div>
            </div>

            
            <div className="mb-12">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Semantic Colors</h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    
                    <div>
                        <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Success</h4>
                        <div className="grid grid-cols-3 gap-2">
                            <div className="color-swatch">
                                <div className="w-full h-16 bg-success-100 rounded-lg border border-gray-200 dark:border-gray-600"></div>
                                <p className="text-xs font-mono mt-1 text-gray-600 dark:text-gray-400">100</p>
                            </div>
                            <div className="color-swatch">
                                <div className="w-full h-16 bg-success-500 rounded-lg border border-gray-200 dark:border-gray-600"></div>
                                <p className="text-xs font-mono mt-1 text-gray-600 dark:text-gray-400">500</p>
                            </div>
                            <div className="color-swatch">
                                <div className="w-full h-16 bg-success-700 rounded-lg border border-gray-200 dark:border-gray-600"></div>
                                <p className="text-xs font-mono mt-1 text-gray-600 dark:text-gray-400">700</p>
                            </div>
                        </div>
                    </div>
                    
                    
                    <div>
                        <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Warning</h4>
                        <div className="grid grid-cols-3 gap-2">
                            <div className="color-swatch">
                                <div className="w-full h-16 bg-warning-100 rounded-lg border border-gray-200 dark:border-gray-600"></div>
                                <p className="text-xs font-mono mt-1 text-gray-600 dark:text-gray-400">100</p>
                            </div>
                            <div className="color-swatch">
                                <div className="w-full h-16 bg-warning-500 rounded-lg border border-gray-200 dark:border-gray-600"></div>
                                <p className="text-xs font-mono mt-1 text-gray-600 dark:text-gray-400">500</p>
                            </div>
                            <div className="color-swatch">
                                <div className="w-full h-16 bg-warning-700 rounded-lg border border-gray-200 dark:border-gray-600"></div>
                                <p className="text-xs font-mono mt-1 text-gray-600 dark:text-gray-400">700</p>
                            </div>
                        </div>
                    </div>
                    
                    
                    <div>
                        <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Danger</h4>
                        <div className="grid grid-cols-3 gap-2">
                            <div className="color-swatch">
                                <div className="w-full h-16 bg-danger-100 rounded-lg border border-gray-200 dark:border-gray-600"></div>
                                <p className="text-xs font-mono mt-1 text-gray-600 dark:text-gray-400">100</p>
                            </div>
                            <div className="color-swatch">
                                <div className="w-full h-16 bg-danger-500 rounded-lg border border-gray-200 dark:border-gray-600"></div>
                                <p className="text-xs font-mono mt-1 text-gray-600 dark:text-gray-400">500</p>
                            </div>
                            <div className="color-swatch">
                                <div className="w-full h-16 bg-danger-700 rounded-lg border border-gray-200 dark:border-gray-600"></div>
                                <p className="text-xs font-mono mt-1 text-gray-600 dark:text-gray-400">700</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            
            <div className="mb-12">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Usage Examples</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    <div className="bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800 rounded-lg p-4">
                        <div className="w-8 h-8 bg-primary-500 rounded-lg mb-3"></div>
                        <h4 className="font-medium text-primary-900 dark:text-primary-100 mb-2">Primary Action</h4>
                        <p className="text-sm text-primary-700 dark:text-primary-300">Main call-to-action buttons and important links</p>
                    </div>
                    
                    <div className="bg-success-50 dark:bg-success-900/20 border border-success-200 dark:border-success-800 rounded-lg p-4">
                        <div className="w-8 h-8 bg-success-500 rounded-lg mb-3"></div>
                        <h4 className="font-medium text-success-900 dark:text-success-100 mb-2">Success States</h4>
                        <p className="text-sm text-success-700 dark:text-success-300">Completed actions, positive feedback</p>
                    </div>
                    
                    <div className="bg-warning-50 dark:bg-warning-900/20 border border-warning-200 dark:border-warning-800 rounded-lg p-4">
                        <div className="w-8 h-8 bg-warning-500 rounded-lg mb-3"></div>
                        <h4 className="font-medium text-warning-900 dark:text-warning-100 mb-2">Warning States</h4>
                        <p className="text-sm text-warning-700 dark:text-warning-300">Caution messages, pending actions</p>
                    </div>
                    
                    <div className="bg-danger-50 dark:bg-danger-900/20 border border-danger-200 dark:border-danger-800 rounded-lg p-4">
                        <div className="w-8 h-8 bg-danger-500 rounded-lg mb-3"></div>
                        <h4 className="font-medium text-danger-900 dark:text-danger-100 mb-2">Error States</h4>
                        <p className="text-sm text-danger-700 dark:text-danger-300">Error messages, destructive actions</p>
                    </div>
                </div>
            </div>
        </div>

        
        <div id="typography" className="tab-content hidden">
            <div className="mb-8">
                <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Typography</h2>
                <p className="text-gray-600 dark:text-gray-400 mb-8">Our typography system uses Inter for UI elements and JetBrains Mono for code.</p>
            </div>

            
            <div className="mb-12">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Font Families</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                        <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Inter (Sans-serif)</h4>
                        <div className="space-y-3">
                            <p className="font-light text-gray-700 dark:text-gray-300">Light 300 - The quick brown fox</p>
                            <p className="font-normal text-gray-700 dark:text-gray-300">Regular 400 - The quick brown fox</p>
                            <p className="font-medium text-gray-700 dark:text-gray-300">Medium 500 - The quick brown fox</p>
                            <p className="font-semibold text-gray-700 dark:text-gray-300">Semibold 600 - The quick brown fox</p>
                            <p className="font-bold text-gray-700 dark:text-gray-300">Bold 700 - The quick brown fox</p>
                            <p className="font-extrabold text-gray-700 dark:text-gray-300">Extrabold 800 - The quick brown fox</p>
                        </div>
                    </div>
                    
                    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                        <h4 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">JetBrains Mono (Monospace)</h4>
                        <div className="space-y-3">
                            <p className="font-mono font-normal text-gray-700 dark:text-gray-300">Regular 400 - const value = 'code';</p>
                            <p className="font-mono font-medium text-gray-700 dark:text-gray-300">Medium 500 - function example() {}</p>
                            <p className="font-mono font-semibold text-gray-700 dark:text-gray-300">Semibold 600 - // Comment text</p>
                        </div>
                    </div>
                </div>
            </div>

            
            <div className="mb-12">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Text Sizes</h3>
                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                    <div className="space-y-6">
                        <div className="flex items-baseline space-x-4">
                            <span className="text-xs font-mono text-gray-500 dark:text-gray-400 w-16">text-xs</span>
                            <span className="text-xs text-gray-900 dark:text-white">Extra small text (12px)</span>
                        </div>
                        <div className="flex items-baseline space-x-4">
                            <span className="text-xs font-mono text-gray-500 dark:text-gray-400 w-16">text-sm</span>
                            <span className="text-sm text-gray-900 dark:text-white">Small text (14px)</span>
                        </div>
                        <div className="flex items-baseline space-x-4">
                            <span className="text-xs font-mono text-gray-500 dark:text-gray-400 w-16">text-base</span>
                            <span className="text-base text-gray-900 dark:text-white">Base text (16px)</span>
                        </div>
                        <div className="flex items-baseline space-x-4">
                            <span className="text-xs font-mono text-gray-500 dark:text-gray-400 w-16">text-lg</span>
                            <span className="text-lg text-gray-900 dark:text-white">Large text (18px)</span>
                        </div>
                        <div className="flex items-baseline space-x-4">
                            <span className="text-xs font-mono text-gray-500 dark:text-gray-400 w-16">text-xl</span>
                            <span className="text-xl text-gray-900 dark:text-white">Extra large text (20px)</span>
                        </div>
                        <div className="flex items-baseline space-x-4">
                            <span className="text-xs font-mono text-gray-500 dark:text-gray-400 w-16">text-2xl</span>
                            <span className="text-2xl text-gray-900 dark:text-white">2X large text (24px)</span>
                        </div>
                        <div className="flex items-baseline space-x-4">
                            <span className="text-xs font-mono text-gray-500 dark:text-gray-400 w-16">text-3xl</span>
                            <span className="text-3xl text-gray-900 dark:text-white">3X large text (30px)</span>
                        </div>
                        <div className="flex items-baseline space-x-4">
                            <span className="text-xs font-mono text-gray-500 dark:text-gray-400 w-16">text-4xl</span>
                            <span className="text-4xl text-gray-900 dark:text-white">4X large text (36px)</span>
                        </div>
                    </div>
                </div>
            </div>

            
            <div className="mb-12">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Typography Hierarchy</h3>
                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                    <div className="space-y-6">
                        <div>
                            <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-2">Page Title (H1)</h1>
                            <code className="text-xs font-mono text-gray-500 dark:text-gray-400">text-4xl font-bold</code>
                        </div>
                        <div>
                            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">Section Title (H2)</h2>
                            <code className="text-xs font-mono text-gray-500 dark:text-gray-400">text-3xl font-bold</code>
                        </div>
                        <div>
                            <h3 className="text-2xl font-semibold text-gray-900 dark:text-white mb-2">Subsection Title (H3)</h3>
                            <code className="text-xs font-mono text-gray-500 dark:text-gray-400">text-2xl font-semibold</code>
                        </div>
                        <div>
                            <h4 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Component Title (H4)</h4>
                            <code className="text-xs font-mono text-gray-500 dark:text-gray-400">text-xl font-semibold</code>
                        </div>
                        <div>
                            <h5 className="text-lg font-medium text-gray-900 dark:text-white mb-2">Card Title (H5)</h5>
                            <code className="text-xs font-mono text-gray-500 dark:text-gray-400">text-lg font-medium</code>
                        </div>
                        <div>
                            <p className="text-base text-gray-700 dark:text-gray-300 mb-2">Body text - Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
                            <code className="text-xs font-mono text-gray-500 dark:text-gray-400">text-base text-gray-700</code>
                        </div>
                        <div>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">Small text - Additional information or secondary content</p>
                            <code className="text-xs font-mono text-gray-500 dark:text-gray-400">text-sm text-gray-600</code>
                        </div>
                        <div>
                            <p className="text-xs text-gray-500 dark:text-gray-500 mb-2">Caption text - Timestamps, metadata, fine print</p>
                            <code className="text-xs font-mono text-gray-500 dark:text-gray-400">text-xs text-gray-500</code>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        
        <div id="spacing" className="tab-content hidden">
            <div className="mb-8">
                <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Spacing System</h2>
                <p className="text-gray-600 dark:text-gray-400 mb-8">Consistent spacing creates visual rhythm and hierarchy in our interfaces.</p>
            </div>

            
            <div className="mb-12">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Spacing Scale</h3>
                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                    <div className="space-y-4">
                        <div className="flex items-center space-x-4">
                            <span className="text-sm font-mono text-gray-500 dark:text-gray-400 w-12">0</span>
                            <div className="w-0 h-4 bg-primary-500"></div>
                            <span className="text-sm text-gray-700 dark:text-gray-300">0px</span>
                        </div>
                        <div className="flex items-center space-x-4">
                            <span className="text-sm font-mono text-gray-500 dark:text-gray-400 w-12">1</span>
                            <div className="w-1 h-4 bg-primary-500"></div>
                            <span className="text-sm text-gray-700 dark:text-gray-300">4px</span>
                        </div>
                        <div className="flex items-center space-x-4">
                            <span className="text-sm font-mono text-gray-500 dark:text-gray-400 w-12">2</span>
                            <div className="w-2 h-4 bg-primary-500"></div>
                            <span className="text-sm text-gray-700 dark:text-gray-300">8px</span>
                        </div>
                        <div className="flex items-center space-x-4">
                            <span className="text-sm font-mono text-gray-500 dark:text-gray-400 w-12">3</span>
                            <div className="w-3 h-4 bg-primary-500"></div>
                            <span className="text-sm text-gray-700 dark:text-gray-300">12px</span>
                        </div>
                        <div className="flex items-center space-x-4">
                            <span className="text-sm font-mono text-gray-500 dark:text-gray-400 w-12">4</span>
                            <div className="w-4 h-4 bg-primary-500"></div>
                            <span className="text-sm text-gray-700 dark:text-gray-300">16px</span>
                        </div>
                        <div className="flex items-center space-x-4">
                            <span className="text-sm font-mono text-gray-500 dark:text-gray-400 w-12">5</span>
                            <div className="w-5 h-4 bg-primary-500"></div>
                            <span className="text-sm text-gray-700 dark:text-gray-300">20px</span>
                        </div>
                        <div className="flex items-center space-x-4">
                            <span className="text-sm font-mono text-gray-500 dark:text-gray-400 w-12">6</span>
                            <div className="w-6 h-4 bg-primary-500"></div>
                            <span className="text-sm text-gray-700 dark:text-gray-300">24px</span>
                        </div>
                        <div className="flex items-center space-x-4">
                            <span className="text-sm font-mono text-gray-500 dark:text-gray-400 w-12">8</span>
                            <div className="w-8 h-4 bg-primary-500"></div>
                            <span className="text-sm text-gray-700 dark:text-gray-300">32px</span>
                        </div>
                        <div className="flex items-center space-x-4">
                            <span className="text-sm font-mono text-gray-500 dark:text-gray-400 w-12">10</span>
                            <div className="w-10 h-4 bg-primary-500"></div>
                            <span className="text-sm text-gray-700 dark:text-gray-300">40px</span>
                        </div>
                        <div className="flex items-center space-x-4">
                            <span className="text-sm font-mono text-gray-500 dark:text-gray-400 w-12">12</span>
                            <div className="w-12 h-4 bg-primary-500"></div>
                            <span className="text-sm text-gray-700 dark:text-gray-300">48px</span>
                        </div>
                        <div className="flex items-center space-x-4">
                            <span className="text-sm font-mono text-gray-500 dark:text-gray-400 w-12">16</span>
                            <div className="w-16 h-4 bg-primary-500"></div>
                            <span className="text-sm text-gray-700 dark:text-gray-300">64px</span>
                        </div>
                        <div className="flex items-center space-x-4">
                            <span className="text-sm font-mono text-gray-500 dark:text-gray-400 w-12">20</span>
                            <div className="w-20 h-4 bg-primary-500"></div>
                            <span className="text-sm text-gray-700 dark:text-gray-300">80px</span>
                        </div>
                        <div className="flex items-center space-x-4">
                            <span className="text-sm font-mono text-gray-500 dark:text-gray-400 w-12">24</span>
                            <div className="w-24 h-4 bg-primary-500"></div>
                            <span className="text-sm text-gray-700 dark:text-gray-300">96px</span>
                        </div>
                    </div>
                </div>
            </div>

            
            <div className="mb-12">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Usage Guidelines</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                        <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Component Spacing</h4>
                        <div className="space-y-3">
                            <div className="flex justify-between items-center">
                                <span className="text-sm text-gray-600 dark:text-gray-400">Between elements</span>
                                <code className="text-xs font-mono bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">space-y-4 (16px)</code>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-sm text-gray-600 dark:text-gray-400">Card padding</span>
                                <code className="text-xs font-mono bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">p-6 (24px)</code>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-sm text-gray-600 dark:text-gray-400">Button padding</span>
                                <code className="text-xs font-mono bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">px-4 py-2 (16px 8px)</code>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-sm text-gray-600 dark:text-gray-400">Section margins</span>
                                <code className="text-xs font-mono bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">mb-8 (32px)</code>
                            </div>
                        </div>
                    </div>
                    
                    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                        <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Layout Spacing</h4>
                        <div className="space-y-3">
                            <div className="flex justify-between items-center">
                                <span className="text-sm text-gray-600 dark:text-gray-400">Page padding</span>
                                <code className="text-xs font-mono bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">px-4 py-8</code>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-sm text-gray-600 dark:text-gray-400">Grid gaps</span>
                                <code className="text-xs font-mono bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">gap-6 (24px)</code>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-sm text-gray-600 dark:text-gray-400">Form spacing</span>
                                <code className="text-xs font-mono bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">space-y-6 (24px)</code>
                            </div>
                            <div className="flex justify-between items-center">
                                <span className="text-sm text-gray-600 dark:text-gray-400">Modal padding</span>
                                <code className="text-xs font-mono bg-gray-100 dark:bg-gray-700 px-2 py-1 rounded">p-6 (24px)</code>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        
        <div id="buttons" className="tab-content hidden">
            <div className="mb-8">
                <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Buttons</h2>
                <p className="text-gray-600 dark:text-gray-400 mb-8">Button components for various actions and states.</p>
            </div>

            
            <div className="mb-12">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Button Variants</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    
                    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                        <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Primary</h4>
                        <div className="space-y-4">
                            <button className="btn-primary">Primary Button</button>
                            <button className="btn-primary" disabled="">Disabled</button>
                            <button className="btn-primary btn-loading">
                                <i data-lucide="loader-2" className="w-4 h-4 animate-spin mr-2"></i>
                                Loading
                            </button>
                        </div>
                        <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-700 rounded text-xs font-mono text-gray-600 dark:text-gray-400">
                            bg-primary-600 hover:bg-primary-700<br />
                            text-white px-4 py-2 rounded-lg
                        </div>
                    </div>
                    
                    
                    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                        <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Secondary</h4>
                        <div className="space-y-4">
                            <button className="btn-secondary">Secondary Button</button>
                            <button className="btn-secondary" disabled="">Disabled</button>
                            <button className="btn-secondary btn-loading">
                                <i data-lucide="loader-2" className="w-4 h-4 animate-spin mr-2"></i>
                                Loading
                            </button>
                        </div>
                        <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-700 rounded text-xs font-mono text-gray-600 dark:text-gray-400">
                            bg-white dark:bg-gray-700<br />
                            border border-gray-300 dark:border-gray-600<br />
                            text-gray-700 dark:text-gray-300
                        </div>
                    </div>
                    
                    
                    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                        <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Outline</h4>
                        <div className="space-y-4">
                            <button className="btn-outline">Outline Button</button>
                            <button className="btn-outline" disabled="">Disabled</button>
                            <button className="btn-outline btn-loading">
                                <i data-lucide="loader-2" className="w-4 h-4 animate-spin mr-2"></i>
                                Loading
                            </button>
                        </div>
                        <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-700 rounded text-xs font-mono text-gray-600 dark:text-gray-400">
                            border-2 border-primary-600<br />
                            text-primary-600 hover:bg-primary-50<br />
                            dark:hover:bg-primary-900/20
                        </div>
                    </div>
                    
                    
                    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                        <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Ghost</h4>
                        <div className="space-y-4">
                            <button className="btn-ghost">Ghost Button</button>
                            <button className="btn-ghost" disabled="">Disabled</button>
                            <button className="btn-ghost btn-loading">
                                <i data-lucide="loader-2" className="w-4 h-4 animate-spin mr-2"></i>
                                Loading
                            </button>
                        </div>
                        <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-700 rounded text-xs font-mono text-gray-600 dark:text-gray-400">
                            text-gray-600 dark:text-gray-400<br />
                            hover:bg-gray-100 dark:hover:bg-gray-700<br />
                            hover:text-gray-900 dark:hover:text-gray-100
                        </div>
                    </div>
                    
                    
                    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                        <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Danger</h4>
                        <div className="space-y-4">
                            <button className="btn-danger">Danger Button</button>
                            <button className="btn-danger" disabled="">Disabled</button>
                            <button className="btn-danger btn-loading">
                                <i data-lucide="loader-2" className="w-4 h-4 animate-spin mr-2"></i>
                                Loading
                            </button>
                        </div>
                        <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-700 rounded text-xs font-mono text-gray-600 dark:text-gray-400">
                            bg-danger-600 hover:bg-danger-700<br />
                            text-white px-4 py-2 rounded-lg
                        </div>
                    </div>
                    
                    
                    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                        <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Success</h4>
                        <div className="space-y-4">
                            <button className="btn-success">Success Button</button>
                            <button className="btn-success" disabled="">Disabled</button>
                            <button className="btn-success btn-loading">
                                <i data-lucide="loader-2" className="w-4 h-4 animate-spin mr-2"></i>
                                Loading
                            </button>
                        </div>
                        <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-700 rounded text-xs font-mono text-gray-600 dark:text-gray-400">
                            bg-success-600 hover:bg-success-700<br />
                            text-white px-4 py-2 rounded-lg
                        </div>
                    </div>
                </div>
            </div>

            
            <div className="mb-12">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Button Sizes</h3>
                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                    <div className="flex flex-wrap items-center gap-4">
                        <button className="btn-primary text-xs px-2 py-1">Extra Small</button>
                        <button className="btn-primary text-sm px-3 py-1.5">Small</button>
                        <button className="btn-primary px-4 py-2">Medium (Default)</button>
                        <button className="btn-primary text-lg px-6 py-3">Large</button>
                        <button className="btn-primary text-xl px-8 py-4">Extra Large</button>
                    </div>
                    <div className="mt-4 p-3 bg-gray-50 dark:bg-gray-700 rounded text-xs font-mono text-gray-600 dark:text-gray-400">
                        XS: text-xs px-2 py-1<br />
                        SM: text-sm px-3 py-1.5<br />
                        MD: px-4 py-2 (default)<br />
                        LG: text-lg px-6 py-3<br />
                        XL: text-xl px-8 py-4
                    </div>
                </div>
            </div>

            
            <div className="mb-12">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Buttons with Icons</h3>
                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                    <div className="flex flex-wrap items-center gap-4">
                        <button className="btn-primary">
                            <i data-lucide="plus" className="w-4 h-4 mr-2"></i>
                            Add Item
                        </button>
                        <button className="btn-secondary">
                            <i data-lucide="download" className="w-4 h-4 mr-2"></i>
                            Download
                        </button>
                        <button className="btn-outline">
                            Edit
                            <i data-lucide="edit" className="w-4 h-4 ml-2"></i>
                        </button>
                        <button className="btn-danger">
                            <i data-lucide="trash-2" className="w-4 h-4 mr-2"></i>
                            Delete
                        </button>
                        <button className="btn-ghost p-2">
                            <i data-lucide="settings" className="w-4 h-4"></i>
                        </button>
                    </div>
                </div>
            </div>

            
            <div className="mb-12">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Button Groups</h3>
                <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                    <div className="space-y-6">
                        
                        <div>
                            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Horizontal Group</h4>
                            <div className="inline-flex rounded-lg border border-gray-300 dark:border-gray-600 overflow-hidden">
                                <button className="px-4 py-2 bg-primary-600 text-white border-r border-gray-300 dark:border-gray-600 hover:bg-primary-700 transition-colors">
                                    <i data-lucide="list" className="w-4 h-4"></i>
                                </button>
                                <button className="px-4 py-2 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 border-r border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors">
                                    <i data-lucide="grid-3x3" className="w-4 h-4"></i>
                                </button>
                                <button className="px-4 py-2 bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600 transition-colors">
                                    <i data-lucide="layout-grid" className="w-4 h-4"></i>
                                </button>
                            </div>
                        </div>
                        
                        
                        <div>
                            <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Action Group</h4>
                            <div className="flex space-x-2">
                                <button className="btn-primary">Save</button>
                                <button className="btn-secondary">Cancel</button>
                                <button className="btn-ghost">
                                    <i data-lucide="more-horizontal" className="w-4 h-4"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        
        <div id="forms" className="tab-content hidden">
            <div className="mb-8">
                <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Form Components</h2>
                <p className="text-gray-600 dark:text-gray-400 mb-8">Form inputs, validation states, and interactive elements.</p>
            </div>

            
            <div className="mb-12">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Input Fields</h3>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                        <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Text Inputs</h4>
                        <div className="space-y-4">
                            <div>
                                <label className="form-label">Default Input</label>
                                <input type="text" className="form-input" placeholder="Enter text..." />
                            </div>
                            <div>
                                <label className="form-label">With Icon</label>
                                <div className="relative">
                                    <input type="text" className="form-input pl-10" placeholder="Search..." />
                                    <i data-lucide="search" className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400"></i>
                                </div>
                            </div>
                            <div>
                                <label className="form-label">Disabled</label>
                                <input type="text" className="form-input" placeholder="Disabled input" disabled="" />
                            </div>
                            <div>
                                <label className="form-label">Error State</label>
                                <input type="text" className="form-input border-danger-300 focus:border-danger-500 focus:ring-danger-500" placeholder="Invalid input" />
                                <p className="form-error">This field is required</p>
                            </div>
                            <div>
                                <label className="form-label">Success State</label>
                                <input type="text" className="form-input border-success-300 focus:border-success-500 focus:ring-success-500" placeholder="Valid input" />
                                <p className="form-success">Looks good!</p>
                            </div>
                        </div>
                    </div>
                    
                    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                        <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Select &amp; Textarea</h4>
                        <div className="space-y-4">
                            <div>
                                <label className="form-label">Select Dropdown</label>
                                <select className="form-select">
                                    <option>Choose an option...</option>
                                    <option>Option 1</option>
                                    <option>Option 2</option>
                                    <option>Option 3</option>
                                </select>
                            </div>
                            <div>
                                <label className="form-label">Multi-select</label>
                                <select className="form-select" multiple="" size="3">
                                    <option>Option 1</option>
                                    <option>Option 2</option>
                                    <option>Option 3</option>
                                    <option>Option 4</option>
                                </select>
                            </div>
                            <div>
                                <label className="form-label">Textarea</label>
                                <textarea className="form-textarea" rows="4" placeholder="Enter your message..."></textarea>
                            </div>
                            <div>
                                <label className="form-label">File Upload</label>
                                <input type="file" className="form-file" />
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            
            <div className="mb-12">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Checkboxes &amp; Radio Buttons</h3>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                        <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Checkboxes</h4>
                        <div className="space-y-3">
                            <label className="form-checkbox">
                                <input type="checkbox" checked="" />
                                <span className="checkmark"></span>
                                <span className="label-text">Checked option</span>
                            </label>
                            <label className="form-checkbox">
                                <input type="checkbox" />
                                <span className="checkmark"></span>
                                <span className="label-text">Unchecked option</span>
                            </label>
                            <label className="form-checkbox">
                                <input type="checkbox" disabled="" />
                                <span className="checkmark"></span>
                                <span className="label-text">Disabled option</span>
                            </label>
                            <label className="form-checkbox">
                                <input type="checkbox" checked="" disabled="" />
                                <span className="checkmark"></span>
                                <span className="label-text">Disabled checked</span>
                            </label>
                        </div>
                    </div>
                    
                    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                        <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Radio Buttons</h4>
                        <div className="space-y-3">
                            <label className="form-radio">
                                <input type="radio" name="radio-group" checked="" />
                                <span className="radiomark"></span>
                                <span className="label-text">Selected option</span>
                            </label>
                            <label className="form-radio">
                                <input type="radio" name="radio-group" />
                                <span className="radiomark"></span>
                                <span className="label-text">Unselected option</span>
                            </label>
                            <label className="form-radio">
                                <input type="radio" name="radio-group" />
                                <span className="radiomark"></span>
                                <span className="label-text">Another option</span>
                            </label>
                            <label className="form-radio">
                                <input type="radio" name="radio-disabled" disabled="" />
                                <span className="radiomark"></span>
                                <span className="label-text">Disabled option</span>
                            </label>
                        </div>
                    </div>
                </div>
            </div>

            
            <div className="mb-12">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Form Layouts</h3>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    
                    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                        <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Vertical Form</h4>
                        <form className="space-y-4">
                            <div>
                                <label className="form-label">Full Name *</label>
                                <input type="text" className="form-input" placeholder="John Doe" required="" />
                            </div>
                            <div>
                                <label className="form-label">Email Address *</label>
                                <input type="email" className="form-input" placeholder="john@example.com" required="" />
                            </div>
                            <div>
                                <label className="form-label">Department</label>
                                <select className="form-select">
                                    <option>Select department...</option>
                                    <option>IT</option>
                                    <option>Finance</option>
                                    <option>HR</option>
                                </select>
                            </div>
                            <div>
                                <label className="form-checkbox">
                                    <input type="checkbox" />
                                    <span className="checkmark"></span>
                                    <span className="label-text">I agree to the terms and conditions</span>
                                </label>
                            </div>
                            <div className="flex space-x-3">
                                <button type="submit" className="btn-primary">Submit</button>
                                <button type="button" className="btn-secondary">Cancel</button>
                            </div>
                        </form>
                    </div>
                    
                    
                    <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6">
                        <h4 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Horizontal Form</h4>
                        <form className="space-y-4">
                            <div className="grid grid-cols-3 gap-4 items-center">
                                <label className="form-label text-right">Name:</label>
                                <input type="text" className="form-input col-span-2" placeholder="John Doe" />
                            </div>
                            <div className="grid grid-cols-3 gap-4 items-center">
                                <label className="form-label text-right">Email:</label>
                                <input type="email" className="form-input col-span-2" placeholder="john@example.com" />
                            </div>
                            <div className="grid grid-cols-3 gap-4 items-center">
                                <label className="form-label text-right">Role:</label>
                                <select className="form-select col-span-2">
                                    <option>Select role...</option>
                                    <option>Admin</option>
                                    <option>User</option>
                                    <option>Viewer</option>
                                </select>
                            </div>
                            <div className="grid grid-cols-3 gap-4 items-center">
                                <div></div>
                                <div className="col-span-2">
                                    <label className="form-checkbox">
                                        <input type="checkbox" />
                                        <span className="checkmark"></span>
                                        <span className="label-text">Send welcome email</span>
                                    </label>
                                </div>
                            </div>
                            <div className="grid grid-cols-3 gap-4 items-center">
                                <div></div>
                                <div className="col-span-2 flex space-x-3">
                                    <button type="submit" className="btn-primary">Save</button>
                                    <button type="button" className="btn-secondary">Reset</button>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>

        
        <div id="cards" className="tab-content hidden">
            <div className="mb-8">
                <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Card Components</h2>
                <p className="text-gray-600 dark:text-gray-400 mb-8">Flexible card layouts for displaying content and data.</p>
            </div>

            
            <div className="mb-12">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Basic Cards</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    
                    <div className="card">
                        <div className="card-header">
                            <h3 className="card-title">Simple Card</h3>
                        </div>
                        <div className="card-body">
                            <p className="text-gray-600 dark:text-gray-400">This is a basic card with header and body content. Perfect for displaying simple information.</p>
                        </div>
                        <div className="card-footer">
                            <button className="btn-primary btn-sm">Action</button>
                        </div>
                    </div>
                    
                    
                    <div className="card">
                        <div className="card-header">
                            <div className="flex items-center space-x-3">
                                <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center">
                                    <i data-lucide="shield-check" className="w-5 h-5 text-primary-600 dark:text-primary-400"></i>
                                </div>
                                <h3 className="card-title">Security Status</h3>
                            </div>
                        </div>
                        <div className="card-body">
                            <p className="text-gray-600 dark:text-gray-400">Your security settings are up to date and properly configured.</p>
                            <div className="mt-3">
                                <span className="badge badge-success">Secure</span>
                            </div>
                        </div>
                    </div>
                    
                    
                    <div className="card">
                        <div className="card-body">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide">Total Users</p>
                                    <p className="text-3xl font-bold text-gray-900 dark:text-white mt-2">2,847</p>
                                    <p className="text-sm text-success-600 dark:text-success-400 mt-1">
                                        <i data-lucide="trending-up" className="w-4 h-4 inline mr-1"></i>
                                        +12% from last month
                                    </p>
                                </div>
                                <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                                    <i data-lucide="users" className="w-6 h-6 text-blue-600 dark:text-blue-400"></i>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            
            <div className="mb-12">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Advanced Cards</h3>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    
                    <div className="card">
                        <div className="card-body">
                            <div className="flex items-start space-x-4">
                                <div className="w-16 h-16 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center text-white font-semibold text-lg">
                                    JD
                                </div>
                                <div className="flex-1">
                                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">John Doe</h3>
                                    <p className="text-gray-600 dark:text-gray-400">Senior BCM Manager</p>
                                    <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">john.doe@company.com</p>
                                    <div className="flex items-center space-x-4 mt-3">
                                        <span className="badge badge-primary">Admin</span>
                                        <span className="text-sm text-gray-500 dark:text-gray-500">Last login: 2 hours ago</span>
                                    </div>
                                </div>
                                <button className="btn-ghost btn-sm">
                                    <i data-lucide="more-vertical" className="w-4 h-4"></i>
                                </button>
                            </div>
                        </div>
                        <div className="card-footer">
                            <div className="flex space-x-2">
                                <button className="btn-primary btn-sm">Edit Profile</button>
                                <button className="btn-secondary btn-sm">View Details</button>
                            </div>
                        </div>
                    </div>
                    
                    
                    <div className="card">
                        <div className="card-header">
                            <div className="flex items-center justify-between">
                                <h3 className="card-title">BIA Progress</h3>
                                <span className="text-2xl font-bold text-primary-600 dark:text-primary-400">68%</span>
                            </div>
                        </div>
                        <div className="card-body">
                            <div className="space-y-4">
                                <div>
                                    <div className="flex justify-between text-sm mb-1">
                                        <span className="text-gray-600 dark:text-gray-400">Planning</span>
                                        <span className="text-gray-900 dark:text-white font-medium">100%</span>
                                    </div>
                                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                                        <div className="bg-success-500 h-2 rounded-full" style={{width: '100%'}}></div>
                                    </div>
                                </div>
                                <div>
                                    <div className="flex justify-between text-sm mb-1">
                                        <span className="text-gray-600 dark:text-gray-400">Data Collection</span>
                                        <span className="text-gray-900 dark:text-white font-medium">75%</span>
                                    </div>
                                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                                        <div className="bg-warning-500 h-2 rounded-full" style={{width: '75%'}}></div>
                                    </div>
                                </div>
                                <div>
                                    <div className="flex justify-between text-sm mb-1">
                                        <span className="text-gray-600 dark:text-gray-400">Analysis</span>
                                        <span className="text-gray-900 dark:text-white font-medium">30%</span>
                                    </div>
                                    <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                                        <div className="bg-danger-500 h-2 rounded-full" style={{width: '30%'}}></div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="card-footer">
                            <button className="btn-primary w-full">Continue BIA</button>
                        </div>
                    </div>
                </div>
            </div>

            
            <div className="mb-12">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Card Variants</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    
                    <div className="card border-success-200 dark:border-success-800">
                        <div className="card-body">
                            <div className="flex items-center space-x-3">
                                <div className="w-10 h-10 bg-success-100 dark:bg-success-900/30 rounded-lg flex items-center justify-center">
                                    <i data-lucide="check-circle" className="w-5 h-5 text-success-600 dark:text-success-400"></i>
                                </div>
                                <div>
                                    <h4 className="font-medium text-success-900 dark:text-success-100">Completed</h4>
                                    <p className="text-sm text-success-700 dark:text-success-300">All tasks done</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    
                    <div className="card border-warning-200 dark:border-warning-800">
                        <div className="card-body">
                            <div className="flex items-center space-x-3">
                                <div className="w-10 h-10 bg-warning-100 dark:bg-warning-900/30 rounded-lg flex items-center justify-center">
                                    <i data-lucide="alert-triangle" className="w-5 h-5 text-warning-600 dark:text-warning-400"></i>
                                </div>
                                <div>
                                    <h4 className="font-medium text-warning-900 dark:text-warning-100">Warning</h4>
                                    <p className="text-sm text-warning-700 dark:text-warning-300">Needs attention</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    
                    <div className="card border-danger-200 dark:border-danger-800">
                        <div className="card-body">
                            <div className="flex items-center space-x-3">
                                <div className="w-10 h-10 bg-danger-100 dark:bg-danger-900/30 rounded-lg flex items-center justify-center">
                                    <i data-lucide="x-circle" className="w-5 h-5 text-danger-600 dark:text-danger-400"></i>
                                </div>
                                <div>
                                    <h4 className="font-medium text-danger-900 dark:text-danger-100">Error</h4>
                                    <p className="text-sm text-danger-700 dark:text-danger-300">Action required</p>
                                </div>
                            </div>
                        </div>
                    </div>
                    
                    
                    <div className="card border-primary-200 dark:border-primary-800">
                        <div className="card-body">
                            <div className="flex items-center space-x-3">
                                <div className="w-10 h-10 bg-primary-100 dark:bg-primary-900/30 rounded-lg flex items-center justify-center">
                                    <i data-lucide="info" className="w-5 h-5 text-primary-600 dark:text-primary-400"></i>
                                </div>
                                <div>
                                    <h4 className="font-medium text-primary-900 dark:text-primary-100">Information</h4>
                                    <p className="text-sm text-primary-700 dark:text-primary-300">For your info</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        
        <div id="modals" className="tab-content hidden">
            <div className="mb-8">
                <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Modal Components</h2>
                <p className="text-gray-600 dark:text-gray-400 mb-8">Modal dialogs for confirmations, forms, and content display.</p>
            </div>

            
            <div className="mb-12">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Modal Examples</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    <button className="btn-primary" onclick="openModal('confirmModal')">Confirmation Modal</button>
                    <button className="btn-secondary" onclick="openModal('formModal')">Form Modal</button>
                    <button className="btn-outline" onclick="openModal('infoModal')">Info Modal</button>
                    <button className="btn-danger" onclick="openModal('deleteModal')">Delete Confirmation</button>
                    <button className="btn-success" onclick="openModal('successModal')">Success Modal</button>
                    <button className="btn-ghost" onclick="openModal('largeModal')">Large Modal</button>
                </div>
            </div>
        </div>

        
        <div id="icons" className="tab-content hidden">
            <div className="mb-8">
                <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Icon Library</h2>
                <p className="text-gray-600 dark:text-gray-400 mb-8">Lucide icons used throughout the platform for consistency.</p>
            </div>

            
            <div className="mb-12">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">Common Icons</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-4">
                    <div className="icon-item">
                        <div className="icon-preview">
                            <i data-lucide="home" className="w-6 h-6"></i>
                        </div>
                        <span className="icon-name">home</span>
                    </div>
                    <div className="icon-item">
                        <div className="icon-preview">
                            <i data-lucide="user" className="w-6 h-6"></i>
                        </div>
                        <span className="icon-name">user</span>
                    </div>
                    <div className="icon-item">
                        <div className="icon-preview">
                            <i data-lucide="settings" className="w-6 h-6"></i>
                        </div>
                        <span className="icon-name">settings</span>
                    </div>
                    <div className="icon-item">
                        <div className="icon-preview">
                            <i data-lucide="search" className="w-6 h-6"></i>
                        </div>
                        <span className="icon-name">search</span>
                    </div>
                    <div className="icon-item">
                        <div className="icon-preview">
                            <i data-lucide="bell" className="w-6 h-6"></i>
                        </div>
                        <span className="icon-name">bell</span>
                    </div>
                    <div className="icon-item">
                        <div className="icon-preview">
                            <i data-lucide="mail" className="w-6 h-6"></i>
                        </div>
                        <span className="icon-name">mail</span>
                    </div>
                    <div className="icon-item">
                        <div className="icon-preview">
                            <i data-lucide="calendar" className="w-6 h-6"></i>
                        </div>
                        <span className="icon-name">calendar</span>
                    </div>
                    <div className="icon-item">
                        <div className="icon-preview">
                            <i data-lucide="file" className="w-6 h-6"></i>
                        </div>
                        <span className="icon-name">file</span>
                    </div>
                    <div className="icon-item">
                        <div className="icon-preview">
                            <i data-lucide="folder" className="w-6 h-6"></i>
                        </div>
                        <span className="icon-name">folder</span>
                    </div>
                    <div className="icon-item">
                        <div className="icon-preview">
                            <i data-lucide="download" className="w-6 h-6"></i>
                        </div>
                        <span className="icon-name">download</span>
                    </div>
                    <div className="icon-item">
                        <div className="icon-preview">
                            <i data-lucide="upload" className="w-6 h-6"></i>
                        </div>
                        <span className="icon-name">upload</span>
                    </div>
                    <div className="icon-item">
                        <div className="icon-preview">
                            <i data-lucide="edit" className="w-6 h-6"></i>
                        </div>
                        <span className="icon-name">edit</span>
                    </div>
                    <div className="icon-item">
                        <div className="icon-preview">
                            <i data-lucide="trash-2" className="w-6 h-6"></i>
                        </div>
                        <span className="icon-name">trash-2</span>
                    </div>
                    <div className="icon-item">
                        <div className="icon-preview">
                            <i data-lucide="plus" className="w-6 h-6"></i>
                        </div>
                        <span className="icon-name">plus</span>
                    </div>
                    <div className="icon-item">
                        <div className="icon-preview">
                            <i data-lucide="minus" className="w-6 h-6"></i>
                        </div>
                        <span className="icon-name">minus</span>
                    </div>
                    <div className="icon-item">
                        <div className="icon-preview">
                            <i data-lucide="x" className="w-6 h-6"></i>
                        </div>
                        <span className="icon-name">x</span>
                    </div>
                    <div className="icon-item">
                        <div className="icon-preview">
                            <i data-lucide="check" className="w-6 h-6"></i>
                        </div>
                        <span className="icon-name">check</span>
                    </div>
                    <div className="icon-item">
                        <div className="icon-preview">
                            <i data-lucide="chevron-right" className="w-6 h-6"></i>
                        </div>
                        <span className="icon-name">chevron-right</span>
                    </div>
                    <div className="icon-item">
                        <div className="icon-preview">
                            <i data-lucide="chevron-left" className="w-6 h-6"></i>
                        </div>
                        <span className="icon-name">chevron-left</span>
                    </div>
                    <div className="icon-item">
                        <div className="icon-preview">
                            <i data-lucide="chevron-up" className="w-6 h-6"></i>
                        </div>
                        <span className="icon-name">chevron-up</span>
                    </div>
                    <div className="icon-item">
                        <div className="icon-preview">
                            <i data-lucide="chevron-down" className="w-6 h-6"></i>
                        </div>
                        <span className="icon-name">chevron-down</span>
                    </div>
                    <div className="icon-item">
                        <div className="icon-preview">
                            <i data-lucide="arrow-right" className="w-6 h-6"></i>
                        </div>
                        <span className="icon-name">arrow-right</span>
                    </div>
                    <div className="icon-item">
                        <div className="icon-preview">
                            <i data-lucide="external-link" className="w-6 h-6"></i>
                        </div>
                        <span className="icon-name">external-link</span>
                    </div>
                    <div className="icon-item">
                        <div className="icon-preview">
                            <i data-lucide="link" className="w-6 h-6"></i>
                        </div>
                        <span className="icon-name">link</span>
                    </div>
                </div>
            </div>

            
            <div className="mb-12">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-6">BCM Specific Icons</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 xl:grid-cols-8 gap-4">
                    <div className="icon-item">
                        <div className="icon-preview">
                            <i data-lucide="shield-check" className="w-6 h-6"></i>
                        </div>
                        <span className="icon-name">shield-check</span>
                    </div>
                    <div className="icon-item">
                        <div className="icon-preview">
                            <i data-lucide="alert-triangle" className="w-6 h-6"></i>
                        </div>
                        <span className="icon-name">alert-triangle</span>
                    </div>
                    <div className="icon-item">
                        <div className="icon-preview">
                            </div></div></div></div></div></main>
    </div>
  );
};

export default Untitled1;