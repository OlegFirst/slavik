export default function handler(req: any, res: any) {
  const data = [
    { id: 1, name: 'Incidents Resolved', value: 5, unit: '' },
    { id: 2, name: 'Exercises Completed', value: 3, unit: '' },
    { id: 3, name: 'Training Completion', value: 80, unit: '%' }
  ]
  res.status(200).json(Array.isArray(data) ? data : [])
}
