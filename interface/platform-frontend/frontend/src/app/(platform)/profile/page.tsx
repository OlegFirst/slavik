import React from 'react';
import {
  User,
  Mail,
  Building2,
  Shield,
  Bell,
  Key,
  Globe,
  Calendar,
  Clock
} from 'lucide-react';

export default function ProfilePage() {
  return (
    <div className="space-y-8 max-w-4xl">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Profile</h1>
        <p className="text-muted-foreground mt-2">
          Manage your account settings and preferences
        </p>
      </div>

      {/* Profile Overview */}
      <div className="rounded-xl border bg-card p-8 shadow-sm">
        <div className="flex items-start gap-6">
          {/* Avatar */}
          <div className="h-24 w-24 rounded-full bg-gradient-to-br from-purple-600 to-blue-600 flex items-center justify-center text-white text-3xl font-bold">
            AU
          </div>

          {/* Info */}
          <div className="flex-1">
            <h2 className="text-2xl font-bold">Admin User</h2>
            <p className="text-muted-foreground mt-1">admin@platform.com</p>

            <div className="flex items-center gap-4 mt-4">
              <div className="flex items-center gap-2 text-sm">
                <Building2 className="h-4 w-4 text-muted-foreground" />
                <span>Default Organization</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <Shield className="h-4 w-4 text-muted-foreground" />
                <span className="bg-purple-500/10 text-purple-600 px-2 py-0.5 rounded-full text-xs font-medium">
                  Super Admin
                </span>
              </div>
            </div>

            <div className="flex gap-3 mt-6">
              <button className="px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors font-medium">
                Edit Profile
              </button>
              <button className="px-4 py-2 rounded-lg border hover:bg-accent transition-colors font-medium">
                Change Password
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Account Information */}
      <div className="rounded-xl border bg-card p-6 shadow-sm">
        <h3 className="font-semibold text-lg mb-6">Account Information</h3>

        <div className="space-y-6">
          <div className="grid gap-6 sm:grid-cols-2">
            <div>
              <label className="text-sm font-medium text-muted-foreground mb-2 block">
                Full Name
              </label>
              <div className="flex items-center gap-3 p-3 rounded-lg border">
                <User className="h-4 w-4 text-muted-foreground" />
                <input
                  type="text"
                  defaultValue="Admin User"
                  className="flex-1 bg-transparent outline-none"
                />
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-muted-foreground mb-2 block">
                Email Address
              </label>
              <div className="flex items-center gap-3 p-3 rounded-lg border">
                <Mail className="h-4 w-4 text-muted-foreground" />
                <input
                  type="email"
                  defaultValue="admin@platform.com"
                  className="flex-1 bg-transparent outline-none"
                />
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-muted-foreground mb-2 block">
                Organization
              </label>
              <div className="flex items-center gap-3 p-3 rounded-lg border">
                <Building2 className="h-4 w-4 text-muted-foreground" />
                <select className="flex-1 bg-transparent outline-none">
                  <option>Default Organization</option>
                  <option>Organization 2</option>
                  <option>Organization 3</option>
                </select>
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-muted-foreground mb-2 block">
                Role
              </label>
              <div className="flex items-center gap-3 p-3 rounded-lg border bg-muted/50">
                <Shield className="h-4 w-4 text-muted-foreground" />
                <span className="text-sm">Super Admin</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Preferences */}
      <div className="rounded-xl border bg-card p-6 shadow-sm">
        <h3 className="font-semibold text-lg mb-6">Preferences</h3>

        <div className="space-y-6">
          {/* Language */}
          <div className="flex items-center justify-between py-3 border-b">
            <div className="flex items-center gap-3">
              <Globe className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="font-medium">Language</p>
                <p className="text-sm text-muted-foreground">
                  Choose your preferred language
                </p>
              </div>
            </div>
            <select className="px-4 py-2 rounded-lg border bg-background">
              <option>English</option>
              <option>Русский</option>
              <option>Deutsch</option>
            </select>
          </div>

          {/* Timezone */}
          <div className="flex items-center justify-between py-3 border-b">
            <div className="flex items-center gap-3">
              <Clock className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="font-medium">Timezone</p>
                <p className="text-sm text-muted-foreground">
                  Set your local timezone
                </p>
              </div>
            </div>
            <select className="px-4 py-2 rounded-lg border bg-background">
              <option>UTC+0</option>
              <option>UTC+3 (Moscow)</option>
              <option>UTC+1 (Berlin)</option>
            </select>
          </div>

          {/* Notifications */}
          <div className="flex items-center justify-between py-3 border-b">
            <div className="flex items-center gap-3">
              <Bell className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="font-medium">Email Notifications</p>
                <p className="text-sm text-muted-foreground">
                  Receive updates via email
                </p>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" defaultChecked className="sr-only peer" />
              <div className="w-11 h-6 bg-muted peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
            </label>
          </div>
        </div>
      </div>

      {/* Security */}
      <div className="rounded-xl border bg-card p-6 shadow-sm">
        <h3 className="font-semibold text-lg mb-6">Security</h3>

        <div className="space-y-6">
          {/* Password */}
          <div className="flex items-center justify-between py-3 border-b">
            <div className="flex items-center gap-3">
              <Key className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="font-medium">Password</p>
                <p className="text-sm text-muted-foreground">
                  Last changed 30 days ago
                </p>
              </div>
            </div>
            <button className="px-4 py-2 rounded-lg border hover:bg-accent transition-colors font-medium">
              Change
            </button>
          </div>

          {/* Two-Factor Auth */}
          <div className="flex items-center justify-between py-3 border-b">
            <div className="flex items-center gap-3">
              <Shield className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="font-medium">Two-Factor Authentication</p>
                <p className="text-sm text-muted-foreground">
                  Add an extra layer of security
                </p>
              </div>
            </div>
            <button className="px-4 py-2 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors font-medium">
              Enable
            </button>
          </div>

          {/* Sessions */}
          <div className="flex items-center justify-between py-3">
            <div className="flex items-center gap-3">
              <Calendar className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="font-medium">Active Sessions</p>
                <p className="text-sm text-muted-foreground">
                  Manage your active sessions
                </p>
              </div>
            </div>
            <button className="px-4 py-2 rounded-lg border hover:bg-accent transition-colors font-medium">
              View All
            </button>
          </div>
        </div>
      </div>

      {/* Account Stats */}
      <div className="rounded-xl border bg-card p-6 shadow-sm">
        <h3 className="font-semibold text-lg mb-6">Account Activity</h3>

        <div className="grid gap-4 sm:grid-cols-3">
          <div className="p-4 rounded-lg bg-muted/50">
            <p className="text-sm text-muted-foreground mb-1">Member Since</p>
            <p className="text-lg font-bold">Jan 2025</p>
          </div>

          <div className="p-4 rounded-lg bg-muted/50">
            <p className="text-sm text-muted-foreground mb-1">Last Login</p>
            <p className="text-lg font-bold">Today, 10:30</p>
          </div>

          <div className="p-4 rounded-lg bg-muted/50">
            <p className="text-sm text-muted-foreground mb-1">Total Actions</p>
            <p className="text-lg font-bold">1,234</p>
          </div>
        </div>
      </div>

      {/* Danger Zone */}
      <div className="rounded-xl border border-red-200 bg-red-50/50 dark:bg-red-950/20 dark:border-red-900 p-6">
        <h3 className="font-semibold text-lg text-red-600 dark:text-red-400 mb-4">
          Danger Zone
        </h3>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium">Delete Account</p>
              <p className="text-sm text-muted-foreground">
                Permanently delete your account and all data
              </p>
            </div>
            <button className="px-4 py-2 rounded-lg bg-red-600 text-white hover:bg-red-700 transition-colors font-medium">
              Delete
            </button>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end gap-3">
        <button className="px-6 py-3 rounded-lg border hover:bg-accent transition-colors font-medium">
          Cancel
        </button>
        <button className="px-6 py-3 rounded-lg bg-primary text-primary-foreground hover:bg-primary/90 transition-colors font-medium">
          Save Changes
        </button>
      </div>
    </div>
  );
}
