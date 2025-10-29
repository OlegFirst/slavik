<template>
  <div class="bcm-base">
    <!-- Header Section -->
    <div class="base-header">
      <div class="container-fluid">
        <div class="row align-items-center">
          <div class="col-md-8">
            <h1 class="page-title">Base Management</h1>
            <p class="page-subtitle">Foundation Settings & Master Data</p>
          </div>
          <div class="col-md-4 text-end">
            <button class="btn btn-primary me-2" @click="showCreateModal = true">
              <i class="fas fa-plus"></i> Add Entry
            </button>
            <button class="btn btn-outline-primary" @click="refreshData">
              <i class="fas fa-sync"></i> Refresh
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Base Overview -->
    <div class="overview-section">
      <div class="container-fluid">
        <div class="row">
          <div class="col-md-3">
            <div class="metric-card primary">
              <div class="metric-icon">
                <i class="fas fa-database"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ baseMetrics.totalRecords }}</h3>
                <p class="metric-label">Total Records</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="metric-card success">
              <div class="metric-icon">
                <i class="fas fa-check-circle"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ baseMetrics.activeRecords }}</h3>
                <p class="metric-label">Active Records</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="metric-card warning">
              <div class="metric-icon">
                <i class="fas fa-sync-alt"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ baseMetrics.recentUpdates }}</h3>
                <p class="metric-label">Recent Updates</p>
              </div>
            </div>
          </div>
          <div class="col-md-3">
            <div class="metric-card info">
              <div class="metric-icon">
                <i class="fas fa-calendar"></i>
              </div>
              <div class="metric-content">
                <h3 class="metric-value">{{ formatDate(baseMetrics.lastSync) }}</h3>
                <p class="metric-label">Last Sync</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Base Management Tabs -->
    <div class="content-section">
      <div class="container-fluid">
        <div class="row">
          <div class="col-12">
            <div class="content-card">
              <div class="card-header">
                <div class="base-tabs">
                  <button
                    v-for="tab in baseTabs"
                    :key="tab.id"
                    class="tab-btn"
                    :class="{ active: activeTab === tab.id }"
                    @click="activeTab = tab.id"
                  >
                    <i :class="tab.icon"></i>
                    {{ tab.name }}
                  </button>
                </div>
              </div>
              <div class="card-body">
                <!-- Organizations Tab -->
                <div v-if="activeTab === 'organizations'" class="tab-content">
                  <div class="table-responsive">
                    <table class="table table-hover">
                      <thead>
                        <tr>
                          <th>Organization</th>
                          <th>Type</th>
                          <th>Status</th>
                          <th>Contact</th>
                          <th>Last Updated</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="org in organizations" :key="org.id">
                          <td>
                            <div class="org-info">
                              <strong>{{ org.name }}</strong>
                              <small class="text-muted d-block">{{ org.description }}</small>
                            </div>
                          </td>
                          <td>
                            <span class="badge bg-primary">{{ org.type }}</span>
                          </td>
                          <td>
                            <span class="status-badge" :class="org.status">{{ org.status }}</span>
                          </td>
                          <td>{{ org.contact_email }}</td>
                          <td>{{ formatDate(org.write_date) }}</td>
                          <td>
                            <div class="action-buttons">
                              <button class="btn btn-sm btn-outline-primary" @click="editEntry(org, 'organization')">
                                <i class="fas fa-edit"></i>
                              </button>
                              <button class="btn btn-sm btn-outline-danger" @click="deleteEntry(org, 'organization')">
                                <i class="fas fa-trash"></i>
                              </button>
                            </div>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                <!-- Locations Tab -->
                <div v-if="activeTab === 'locations'" class="tab-content">
                  <div class="table-responsive">
                    <table class="table table-hover">
                      <thead>
                        <tr>
                          <th>Location</th>
                          <th>Address</th>
                          <th>Type</th>
                          <th>Capacity</th>
                          <th>Status</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="location in locations" :key="location.id">
                          <td>
                            <div class="location-info">
                              <strong>{{ location.name }}</strong>
                              <small class="text-muted d-block">{{ location.code }}</small>
                            </div>
                          </td>
                          <td>{{ location.address }}</td>
                          <td>
                            <span class="badge bg-info">{{ location.type }}</span>
                          </td>
                          <td>{{ location.capacity || 'N/A' }}</td>
                          <td>
                            <span class="status-badge" :class="location.status">{{ location.status }}</span>
                          </td>
                          <td>
                            <div class="action-buttons">
                              <button class="btn btn-sm btn-outline-primary" @click="editEntry(location, 'location')">
                                <i class="fas fa-edit"></i>
                              </button>
                              <button class="btn btn-sm btn-outline-danger" @click="deleteEntry(location, 'location')">
                                <i class="fas fa-trash"></i>
                              </button>
                            </div>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                <!-- Assets Tab -->
                <div v-if="activeTab === 'assets'" class="tab-content">
                  <div class="table-responsive">
                    <table class="table table-hover">
                      <thead>
                        <tr>
                          <th>Asset</th>
                          <th>Category</th>
                          <th>Criticality</th>
                          <th>Owner</th>
                          <th>Status</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="asset in assets" :key="asset.id">
                          <td>
                            <div class="asset-info">
                              <strong>{{ asset.name }}</strong>
                              <small class="text-muted d-block">{{ asset.asset_id }}</small>
                            </div>
                          </td>
                          <td>
                            <span class="badge bg-secondary">{{ asset.category }}</span>
                          </td>
                          <td>
                            <span class="criticality-badge" :class="asset.criticality">{{ asset.criticality }}</span>
                          </td>
                          <td>{{ asset.owner_name }}</td>
                          <td>
                            <span class="status-badge" :class="asset.status">{{ asset.status }}</span>
                          </td>
                          <td>
                            <div class="action-buttons">
                              <button class="btn btn-sm btn-outline-primary" @click="editEntry(asset, 'asset')">
                                <i class="fas fa-edit"></i>
                              </button>
                              <button class="btn btn-sm btn-outline-danger" @click="deleteEntry(asset, 'asset')">
                                <i class="fas fa-trash"></i>
                              </button>
                            </div>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                <!-- Contacts Tab -->
                <div v-if="activeTab === 'contacts'" class="tab-content">
                  <div class="table-responsive">
                    <table class="table table-hover">
                      <thead>
                        <tr>
                          <th>Contact</th>
                          <th>Role</th>
                          <th>Organization</th>
                          <th>Phone</th>
                          <th>Email</th>
                          <th>Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="contact in contacts" :key="contact.id">
                          <td>
                            <div class="contact-info">
                              <strong>{{ contact.name }}</strong>
                              <small class="text-muted d-block">{{ contact.title }}</small>
                            </div>
                          </td>
                          <td>
                            <span class="badge bg-success">{{ contact.role }}</span>
                          </td>
                          <td>{{ contact.organization }}</td>
                          <td>{{ contact.phone }}</td>
                          <td>{{ contact.email }}</td>
                          <td>
                            <div class="action-buttons">
                              <button class="btn btn-sm btn-outline-primary" @click="editEntry(contact, 'contact')">
                                <i class="fas fa-edit"></i>
                              </button>
                              <button class="btn btn-sm btn-outline-danger" @click="deleteEntry(contact, 'contact')">
                                <i class="fas fa-trash"></i>
                              </button>
                            </div>
                          </td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div class="modal fade" :class="{ show: showCreateModal }" tabindex="-1" v-if="showCreateModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">{{ editingEntry ? 'Edit' : 'Add' }} {{ currentEntryType }}</h5>
            <button type="button" class="btn-close" @click="closeModal"></button>
          </div>
          <div class="modal-body">
            <!-- Dynamic form based on entry type -->
            <form @submit.prevent="saveEntry">
              <div v-if="currentEntryType === 'organization'">
                <div class="row">
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Name *</label>
                      <input type="text" class="form-control" v-model="currentEntry.name" required>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Type</label>
                      <select class="form-select" v-model="currentEntry.type">
                        <option value="internal">Internal</option>
                        <option value="external">External</option>
                        <option value="vendor">Vendor</option>
                        <option value="partner">Partner</option>
                      </select>
                    </div>
                  </div>
                </div>
                <div class="mb-3">
                  <label class="form-label">Description</label>
                  <textarea class="form-control" rows="3" v-model="currentEntry.description"></textarea>
                </div>
                <div class="mb-3">
                  <label class="form-label">Contact Email</label>
                  <input type="email" class="form-control" v-model="currentEntry.contact_email">
                </div>
              </div>

              <div v-if="currentEntryType === 'location'">
                <div class="row">
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Name *</label>
                      <input type="text" class="form-control" v-model="currentEntry.name" required>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Code</label>
                      <input type="text" class="form-control" v-model="currentEntry.code">
                    </div>
                  </div>
                </div>
                <div class="mb-3">
                  <label class="form-label">Address</label>
                  <textarea class="form-control" rows="2" v-model="currentEntry.address"></textarea>
                </div>
                <div class="row">
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Type</label>
                      <select class="form-select" v-model="currentEntry.type">
                        <option value="office">Office</option>
                        <option value="warehouse">Warehouse</option>
                        <option value="factory">Factory</option>
                        <option value="datacenter">Data Center</option>
                      </select>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Capacity</label>
                      <input type="number" class="form-control" v-model="currentEntry.capacity">
                    </div>
                  </div>
                </div>
              </div>

              <!-- Similar forms for asset and contact types -->
              <div v-if="currentEntryType === 'asset'">
                <div class="row">
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Name *</label>
                      <input type="text" class="form-control" v-model="currentEntry.name" required>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Asset ID</label>
                      <input type="text" class="form-control" v-model="currentEntry.asset_id">
                    </div>
                  </div>
                </div>
                <div class="row">
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Category</label>
                      <select class="form-select" v-model="currentEntry.category">
                        <option value="hardware">Hardware</option>
                        <option value="software">Software</option>
                        <option value="data">Data</option>
                        <option value="facility">Facility</option>
                      </select>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Criticality</label>
                      <select class="form-select" v-model="currentEntry.criticality">
                        <option value="critical">Critical</option>
                        <option value="high">High</option>
                        <option value="medium">Medium</option>
                        <option value="low">Low</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>

              <div v-if="currentEntryType === 'contact'">
                <div class="row">
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Name *</label>
                      <input type="text" class="form-control" v-model="currentEntry.name" required>
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Title</label>
                      <input type="text" class="form-control" v-model="currentEntry.title">
                    </div>
                  </div>
                </div>
                <div class="row">
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Phone</label>
                      <input type="tel" class="form-control" v-model="currentEntry.phone">
                    </div>
                  </div>
                  <div class="col-md-6">
                    <div class="mb-3">
                      <label class="form-label">Email</label>
                      <input type="email" class="form-control" v-model="currentEntry.email">
                    </div>
                  </div>
                </div>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" @click="closeModal">Cancel</button>
            <button type="button" class="btn btn-primary" @click="saveEntry" :disabled="saving">
              {{ saving ? 'Saving...' : 'Save' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import bcmBaseService from '@/services/bcmBase'
import { useToast } from 'vue-toastification'

export default {
  name: 'BCMBase',
  setup() {
    const toast = useToast()

    // Reactive data
    const loading = ref(false)
    const saving = ref(false)
    const showCreateModal = ref(false)
    const editingEntry = ref(false)
    const activeTab = ref('organizations')
    const currentEntryType = ref('')

    const baseMetrics = reactive({
      totalRecords: 0,
      activeRecords: 0,
      recentUpdates: 0,
      lastSync: null
    })

    const currentEntry = reactive({})

    const baseTabs = ref([
      { id: 'organizations', name: 'Organizations', icon: 'fas fa-building' },
      { id: 'locations', name: 'Locations', icon: 'fas fa-map-marker-alt' },
      { id: 'assets', name: 'Assets', icon: 'fas fa-server' },
      { id: 'contacts', name: 'Contacts', icon: 'fas fa-users' }
    ])

    const organizations = ref([])
    const locations = ref([])
    const assets = ref([])
    const contacts = ref([])

    // Methods
    const loadBaseData = async () => {
      loading.value = true
      try {
        const data = await bcmBaseService.getBaseData()
        organizations.value = data.organizations
        locations.value = data.locations
        assets.value = data.assets
        contacts.value = data.contacts

        baseMetrics.totalRecords = data.metrics.total_records
        baseMetrics.activeRecords = data.metrics.active_records
        baseMetrics.recentUpdates = data.metrics.recent_updates
        baseMetrics.lastSync = data.metrics.last_sync
      } catch (error) {
        toast.error('Failed to load base data')
      } finally {
        loading.value = false
      }
    }

    const refreshData = () => {
      loadBaseData()
    }

    const editEntry = (entry, type) => {
      editingEntry.value = true
      currentEntryType.value = type
      Object.assign(currentEntry, entry)
      showCreateModal.value = true
    }

    const saveEntry = async () => {
      saving.value = true
      try {
        if (editingEntry.value) {
          await bcmBaseService.updateEntry(currentEntryType.value, currentEntry.id, currentEntry)
          toast.success('Entry updated successfully')
        } else {
          await bcmBaseService.createEntry(currentEntryType.value, currentEntry)
          toast.success('Entry created successfully')
        }
        closeModal()
        loadBaseData()
      } catch (error) {
        toast.error('Failed to save entry')
      } finally {
        saving.value = false
      }
    }

    const deleteEntry = async (entry, type) => {
      if (confirm(`Are you sure you want to delete ${entry.name}?`)) {
        try {
          await bcmBaseService.deleteEntry(type, entry.id)
          toast.success('Entry deleted successfully')
          loadBaseData()
        } catch (error) {
          toast.error('Failed to delete entry')
        }
      }
    }

    const closeModal = () => {
      showCreateModal.value = false
      editingEntry.value = false
      currentEntryType.value = ''
      Object.keys(currentEntry).forEach(key => delete currentEntry[key])
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    }

    // Lifecycle
    onMounted(() => {
      loadBaseData()
    })

    return {
      // Data
      loading,
      saving,
      showCreateModal,
      editingEntry,
      activeTab,
      currentEntryType,
      baseMetrics,
      currentEntry,
      baseTabs,
      organizations,
      locations,
      assets,
      contacts,

      // Methods
      refreshData,
      editEntry,
      saveEntry,
      deleteEntry,
      closeModal,
      formatDate
    }
  }
}
</script>

<style scoped>
/* Reusing Anthropic color scheme and styling patterns */
:root {
  --anthropic-orange: #FF6B35;
  --anthropic-blue: #4A90E2;
  --anthropic-dark: #1A1A1A;
  --anthropic-light: #F8F9FA;
  --anthropic-success: #28A745;
  --anthropic-warning: #FFC107;
  --anthropic-danger: #DC3545;
}

.bcm-base {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--anthropic-light) 0%, #E8F2FF 100%);
}

.base-header {
  background: white;
  border-bottom: 2px solid var(--anthropic-blue);
  padding: 2rem 0;
  margin-bottom: 2rem;
}

.page-title {
  color: var(--anthropic-dark);
  font-weight: 700;
  font-size: 2.5rem;
  margin: 0;
}

.criticality-badge.critical {
  background: var(--anthropic-danger);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
}

.criticality-badge.high {
  background: var(--anthropic-warning);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
}

.criticality-badge.medium {
  background: var(--anthropic-blue);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
}

.criticality-badge.low {
  background: var(--anthropic-success);
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
}

/* Additional styling following the same patterns as previous components */
</style>