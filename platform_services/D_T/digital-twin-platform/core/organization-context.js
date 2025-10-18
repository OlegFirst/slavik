/**
 * Organization Context - Standalone Mock
 */

export class UniversalOrganizationContext {
    constructor(organizationId) {
        this.organizationId = organizationId;
        this.data = {
            id: organizationId,
            name: 'Demo Organization',
            type: 'non-profit',
            mission: 'Making a difference',
            employees: 50,
            departments: []
        };
    }

    async initialize() {
        return true;
    }

    async getData() {
        return this.data;
    }

    async updateData(updates) {
        Object.assign(this.data, updates);
        return this.data;
    }
}

export default UniversalOrganizationContext;