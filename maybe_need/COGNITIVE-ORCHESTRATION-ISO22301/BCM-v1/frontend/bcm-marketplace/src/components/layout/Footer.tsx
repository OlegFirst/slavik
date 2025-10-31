import React from 'react'
import Link from 'next/link'

export function Footer() {
  return (
    <footer className="bg-gray-900 text-white">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Company Info */}
          <div className="col-span-1">
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">BCM</span>
              </div>
              <span className="text-xl font-bold">Marketplace</span>
            </div>
            <p className="text-gray-400 text-sm mb-4">
              Global marketplace for Business Continuity Management professionals.
            </p>
            <div className="flex space-x-4">
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <span className="sr-only">Facebook</span>
                {/* Facebook icon */}
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <span className="sr-only">LinkedIn</span>
                {/* LinkedIn icon */}
              </a>
              <a href="#" className="text-gray-400 hover:text-white transition-colors">
                <span className="sr-only">Twitter</span>
                {/* Twitter icon */}
              </a>
            </div>
          </div>

          {/* For Clients */}
          <div className="col-span-1">
            <h3 className="text-lg font-semibold mb-4">For Clients</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/specialists" className="text-gray-400 hover:text-white transition-colors">
                  Find Specialists
                </Link>
              </li>
              <li>
                <Link href="/client/create-request" className="text-gray-400 hover:text-white transition-colors">
                  Post Project
                </Link>
              </li>
              <li>
                <Link href="/how-it-works" className="text-gray-400 hover:text-white transition-colors">
                  How it Works
                </Link>
              </li>
            </ul>
          </div>

          {/* For Specialists */}
          <div className="col-span-1">
            <h3 className="text-lg font-semibold mb-4">For Specialists</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/specialist/register" className="text-gray-400 hover:text-white transition-colors">
                  Join as Expert
                </Link>
              </li>
              <li>
                <Link href="/requests" className="text-gray-400 hover:text-white transition-colors">
                  Browse Projects
                </Link>
              </li>
              <li>
                <Link href="/community" className="text-gray-400 hover:text-white transition-colors">
                  Community
                </Link>
              </li>
            </ul>
          </div>

          {/* Support */}
          <div className="col-span-1">
            <h3 className="text-lg font-semibold mb-4">Support</h3>
            <ul className="space-y-2">
              <li>
                <Link href="/help" className="text-gray-400 hover:text-white transition-colors">
                  Help Center
                </Link>
              </li>
              <li>
                <Link href="/contact" className="text-gray-400 hover:text-white transition-colors">
                  Contact Us
                </Link>
              </li>
              <li>
                <Link href="/privacy" className="text-gray-400 hover:text-white transition-colors">
                  Privacy Policy
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-8 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <p className="text-gray-400 text-sm">
              © 2025 BCM Marketplace. All rights reserved.
            </p>
            <div className="flex space-x-6 mt-4 md:mt-0">
              <Link href="/privacy" className="text-gray-400 hover:text-white text-sm transition-colors">
                Privacy
              </Link>
              <Link href="/terms" className="text-gray-400 hover:text-white text-sm transition-colors">
                Terms
              </Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  )
}