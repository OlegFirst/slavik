# -*- coding: utf-8 -*-

import json
import hashlib
import base64
import logging
import uuid
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import jsonschema

_logger = logging.getLogger(__name__)

# Import compression libraries with fallbacks
try:
    import lz4.frame as lz4
    HAS_LZ4 = True
except ImportError:
    HAS_LZ4 = False
    _logger.warning("lz4 not available. Install with: pip install lz4")

try:
    import zstandard as zstd
    HAS_ZSTD = True
except ImportError:
    HAS_ZSTD = False
    _logger.warning("zstandard not available. Install with: pip install zstandard")

try:
    import brotli
    HAS_BROTLI = True
except ImportError:
    HAS_BROTLI = False
    _logger.warning("brotli not available. Install with: pip install brotli")

import gzip
import zlib


class TwinDataPackage(models.Model):
    _name = 'bcm.twin.data.package'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'BCM Digital Twin Data Package'
    _order = 'created_date desc, id desc'
    _rec_name = 'package_id'

    # Core Package Information
    package_id = fields.Char(
        string='Package ID',
        required=True,
        default=lambda self: self._generate_package_id(),
        copy=False,
        tracking=True,
        help="Unique identifier for this data package"
    )

    version = fields.Integer(
        string='Version',
        default=1,
        required=True,
        tracking=True,
        help="Version number for package compatibility"
    )

    # Compression Configuration
    compression_type = fields.Selection([
        ('lz4', 'LZ4 (Fast)'),
        ('zstd', 'Zstandard (Balanced)'),
        ('brotli', 'Brotli (High Compression)'),
        ('gzip', 'Gzip (Compatible)'),
        ('zlib', 'Zlib (Standard)'),
        ('none', 'No Compression')
    ], string='Compression Algorithm',
       default='zstd',
       required=True,
       tracking=True,
       help="Algorithm used for data compression")

    compression_level = fields.Integer(
        string='Compression Level',
        default=3,
        help="Compression level (1-22 for zstd, 1-9 for others)"
    )

    # Data Storage
    data_payload = fields.Binary(
        string='Compressed Data',
        help="Compressed data payload"
    )

    data_hash = fields.Char(
        string='Data Hash (SHA-256)',
        readonly=True,
        help="SHA-256 hash for data integrity verification"
    )

    # Validation Schema
    validation_schema = fields.Text(
        string='JSON Schema',
        help="JSON schema for data validation"
    )

    schema_version = fields.Char(
        string='Schema Version',
        default='1.0',
        help="Version of the validation schema"
    )

    # Size Metrics
    size_original = fields.Integer(
        string='Original Size (bytes)',
        readonly=True,
        help="Size of data before compression"
    )

    size_compressed = fields.Integer(
        string='Compressed Size (bytes)',
        readonly=True,
        help="Size of data after compression"
    )

    compression_ratio = fields.Float(
        string='Compression Ratio',
        compute='_compute_compression_ratio',
        store=True,
        help="Compression ratio (original/compressed)"
    )

    compression_percentage = fields.Float(
        string='Space Saved (%)',
        compute='_compute_compression_percentage',
        store=True,
        help="Percentage of space saved by compression"
    )

    # Metadata
    created_by = fields.Many2one(
        'res.users',
        string='Created By',
        default=lambda self: self.env.user,
        readonly=True
    )

    created_date = fields.Datetime(
        string='Created Date',
        default=fields.Datetime.now,
        readonly=True
    )

    transport_metadata = fields.Text(
        string='Transport Metadata',
        help="JSON metadata for transport optimization"
    )

    # Twin Relations
    source_twin_id = fields.Many2one(
        'bcm.digital.twin.organization',
        string='Source Twin',
        help="Digital twin this package was created from"
    )

    target_twin_id = fields.Many2one(
        'bcm.digital.twin.organization',
        string='Target Twin',
        help="Digital twin this package will be extracted to"
    )

    # Status and Validation
    package_status = fields.Selection([
        ('draft', 'Draft'),
        ('compressed', 'Compressed'),
        ('validated', 'Validated'),
        ('transported', 'In Transport'),
        ('extracted', 'Extracted'),
        ('error', 'Error')
    ], string='Package Status',
       default='draft',
       tracking=True)

    validation_status = fields.Selection([
        ('pending', 'Pending'),
        ('valid', 'Valid'),
        ('invalid', 'Invalid'),
        ('error', 'Validation Error')
    ], string='Validation Status',
       default='pending',
       tracking=True)

    error_message = fields.Text(
        string='Error Message',
        readonly=True,
        help="Error details if validation or processing fails"
    )

    # Content Type Classification
    content_type = fields.Selection([
        ('full_twin', 'Complete Digital Twin'),
        ('simulation_data', 'Simulation Results'),
        ('configuration', 'Configuration Data'),
        ('ai_insights', 'AI Analysis Results'),
        ('delta_update', 'Incremental Update'),
        ('backup', 'Backup Data'),
        ('custom', 'Custom Data')
    ], string='Content Type',
       default='full_twin',
       required=True,
       help="Type of data contained in this package")

    # Network Optimization
    network_priority = fields.Selection([
        ('low', 'Low Priority'),
        ('normal', 'Normal'),
        ('high', 'High Priority'),
        ('critical', 'Critical')
    ], string='Network Priority',
       default='normal',
       help="Priority for network transport")

    chunk_size = fields.Integer(
        string='Chunk Size (KB)',
        default=1024,
        help="Size of chunks for network transfer"
    )

    # Computed Fields
    @api.depends('size_original', 'size_compressed')
    def _compute_compression_ratio(self):
        for record in self:
            if record.size_compressed and record.size_compressed > 0:
                record.compression_ratio = record.size_original / record.size_compressed
            else:
                record.compression_ratio = 0.0

    @api.depends('size_original', 'size_compressed')
    def _compute_compression_percentage(self):
        for record in self:
            if record.size_original and record.size_original > 0:
                saved = record.size_original - record.size_compressed
                record.compression_percentage = (saved / record.size_original) * 100
            else:
                record.compression_percentage = 0.0

    # Core Methods
    def _generate_package_id(self):
        """Generate unique package ID"""
        return f"PKG-{uuid.uuid4().hex[:12].upper()}"

    def _get_available_algorithms(self):
        """Get list of available compression algorithms"""
        algorithms = [('none', 'No Compression'), ('gzip', 'Gzip'), ('zlib', 'Zlib')]

        if HAS_LZ4:
            algorithms.append(('lz4', 'LZ4'))
        if HAS_ZSTD:
            algorithms.append(('zstd', 'Zstandard'))
        if HAS_BROTLI:
            algorithms.append(('brotli', 'Brotli'))

        return algorithms

    def compress_data(self, data, algorithm=None):
        """
        Compress data using specified algorithm

        Args:
            data: Data to compress (string or bytes)
            algorithm: Compression algorithm to use

        Returns:
            tuple: (compressed_data, original_size, compressed_size)
        """
        self.ensure_one()

        algorithm = algorithm or self.compression_type

        # Convert data to bytes if needed
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        elif isinstance(data, dict):
            data_bytes = json.dumps(data, ensure_ascii=False).encode('utf-8')
        else:
            data_bytes = data

        original_size = len(data_bytes)

        try:
            if algorithm == 'lz4' and HAS_LZ4:
                compressed_data = lz4.compress(data_bytes, compression_level=self.compression_level)
            elif algorithm == 'zstd' and HAS_ZSTD:
                cctx = zstd.ZstdCompressor(level=self.compression_level)
                compressed_data = cctx.compress(data_bytes)
            elif algorithm == 'brotli' and HAS_BROTLI:
                level = min(11, max(0, self.compression_level))
                compressed_data = brotli.compress(data_bytes, quality=level)
            elif algorithm == 'gzip':
                level = min(9, max(1, self.compression_level))
                compressed_data = gzip.compress(data_bytes, compresslevel=level)
            elif algorithm == 'zlib':
                level = min(9, max(1, self.compression_level))
                compressed_data = zlib.compress(data_bytes, level=level)
            elif algorithm == 'none':
                compressed_data = data_bytes
            else:
                raise UserError(_("Compression algorithm '%s' is not available") % algorithm)

            compressed_size = len(compressed_data)

            # Generate hash for integrity
            data_hash = hashlib.sha256(data_bytes).hexdigest()

            # Update package data
            self.write({
                'data_payload': base64.b64encode(compressed_data),
                'data_hash': data_hash,
                'size_original': original_size,
                'size_compressed': compressed_size,
                'package_status': 'compressed'
            })

            _logger.info(f"Compressed {original_size} bytes to {compressed_size} bytes using {algorithm}")

            return compressed_data, original_size, compressed_size

        except Exception as e:
            self.write({
                'package_status': 'error',
                'error_message': str(e)
            })
            _logger.error(f"Compression failed: {str(e)}")
            raise UserError(_("Compression failed: %s") % str(e))

    def decompress_data(self):
        """
        Decompress data and validate integrity

        Returns:
            bytes: Decompressed data
        """
        self.ensure_one()

        if not self.data_payload:
            raise UserError(_("No compressed data available"))

        try:
            compressed_data = base64.b64decode(self.data_payload)

            if self.compression_type == 'lz4' and HAS_LZ4:
                decompressed_data = lz4.decompress(compressed_data)
            elif self.compression_type == 'zstd' and HAS_ZSTD:
                dctx = zstd.ZstdDecompressor()
                decompressed_data = dctx.decompress(compressed_data)
            elif self.compression_type == 'brotli' and HAS_BROTLI:
                decompressed_data = brotli.decompress(compressed_data)
            elif self.compression_type == 'gzip':
                decompressed_data = gzip.decompress(compressed_data)
            elif self.compression_type == 'zlib':
                decompressed_data = zlib.decompress(compressed_data)
            elif self.compression_type == 'none':
                decompressed_data = compressed_data
            else:
                raise UserError(_("Unsupported compression type: %s") % self.compression_type)

            # Validate integrity
            if not self.validate_integrity(decompressed_data):
                raise UserError(_("Data integrity validation failed"))

            _logger.info(f"Successfully decompressed {len(decompressed_data)} bytes")
            return decompressed_data

        except Exception as e:
            self.write({
                'package_status': 'error',
                'error_message': str(e)
            })
            _logger.error(f"Decompression failed: {str(e)}")
            raise UserError(_("Decompression failed: %s") % str(e))

    def validate_integrity(self, data=None):
        """
        Validate data integrity using hash verification

        Args:
            data: Data to validate (if None, decompresses first)

        Returns:
            bool: True if validation passes
        """
        self.ensure_one()

        try:
            if data is None:
                data = self.decompress_data()

            if isinstance(data, str):
                data = data.encode('utf-8')

            calculated_hash = hashlib.sha256(data).hexdigest()

            if calculated_hash == self.data_hash:
                self.validation_status = 'valid'
                return True
            else:
                self.validation_status = 'invalid'
                self.error_message = "Hash mismatch: data may be corrupted"
                return False

        except Exception as e:
            self.validation_status = 'error'
            self.error_message = str(e)
            _logger.error(f"Integrity validation failed: {str(e)}")
            return False

    def validate_schema(self, data=None):
        """
        Validate data against JSON schema

        Args:
            data: Data to validate (if None, decompresses and parses first)

        Returns:
            bool: True if schema validation passes
        """
        self.ensure_one()

        if not self.validation_schema:
            return True  # No schema to validate against

        try:
            if data is None:
                decompressed = self.decompress_data()
                if isinstance(decompressed, bytes):
                    data = json.loads(decompressed.decode('utf-8'))
                else:
                    data = json.loads(decompressed)

            schema = json.loads(self.validation_schema)
            jsonschema.validate(data, schema)

            return True

        except jsonschema.ValidationError as e:
            self.validation_status = 'invalid'
            self.error_message = f"Schema validation failed: {str(e)}"
            return False
        except Exception as e:
            self.validation_status = 'error'
            self.error_message = f"Schema validation error: {str(e)}"
            return False

    def optimize_for_transport(self):
        """
        Optimize package for network transport

        Returns:
            dict: Transport optimization metadata
        """
        self.ensure_one()

        transport_config = {
            'package_id': self.package_id,
            'version': self.version,
            'compression_type': self.compression_type,
            'size_compressed': self.size_compressed,
            'chunk_size': self.chunk_size * 1024,  # Convert KB to bytes
            'priority': self.network_priority,
            'content_type': self.content_type,
            'created_date': self.created_date.isoformat(),
            'hash': self.data_hash,
            'schema_version': self.schema_version
        }

        # Calculate optimal chunk strategy
        if self.size_compressed > 10 * 1024 * 1024:  # > 10MB
            transport_config['use_chunking'] = True
            transport_config['chunk_count'] = (self.size_compressed // transport_config['chunk_size']) + 1
        else:
            transport_config['use_chunking'] = False
            transport_config['chunk_count'] = 1

        # Add compression efficiency metrics
        transport_config['compression_ratio'] = self.compression_ratio
        transport_config['compression_percentage'] = self.compression_percentage

        # Update transport metadata
        self.transport_metadata = json.dumps(transport_config, indent=2)
        self.package_status = 'validated'

        _logger.info(f"Package {self.package_id} optimized for transport")

        return transport_config

    def create_package_from_twin(self, twin_id, content_type='full_twin', compression_type=None):
        """
        Create a data package from a digital twin

        Args:
            twin_id: ID of the digital twin
            content_type: Type of content to package
            compression_type: Compression algorithm to use

        Returns:
            dict: Package creation result
        """
        twin = self.env['bcm.digital.twin.organization'].browse(twin_id)
        if not twin.exists():
            raise UserError(_("Digital twin not found"))

        compression_type = compression_type or self.compression_type

        try:
            # Prepare twin data based on content type
            if content_type == 'full_twin':
                twin_data = self._extract_full_twin_data(twin)
            elif content_type == 'simulation_data':
                twin_data = self._extract_simulation_data(twin)
            elif content_type == 'configuration':
                twin_data = self._extract_configuration_data(twin)
            elif content_type == 'ai_insights':
                twin_data = self._extract_ai_insights(twin)
            else:
                raise UserError(_("Unsupported content type: %s") % content_type)

            # Set package metadata
            self.write({
                'source_twin_id': twin_id,
                'content_type': content_type,
                'compression_type': compression_type
            })

            # Compress the data
            self.compress_data(twin_data, compression_type)

            # Optimize for transport
            transport_config = self.optimize_for_transport()

            # Log success
            self.message_post(
                body=_("Package created from twin '%s' using %s compression") % (twin.name, compression_type),
                message_type='notification'
            )

            return {
                'success': True,
                'package_id': self.package_id,
                'original_size': self.size_original,
                'compressed_size': self.size_compressed,
                'compression_ratio': self.compression_ratio,
                'transport_config': transport_config
            }

        except Exception as e:
            self.write({
                'package_status': 'error',
                'error_message': str(e)
            })
            _logger.error(f"Failed to create package from twin {twin_id}: {str(e)}")
            raise UserError(_("Failed to create package: %s") % str(e))

    def extract_to_twin(self, twin_id, merge_strategy='replace'):
        """
        Extract package data to a digital twin

        Args:
            twin_id: ID of the target digital twin
            merge_strategy: How to merge data ('replace', 'merge', 'update')

        Returns:
            dict: Extraction result
        """
        twin = self.env['bcm.digital.twin.organization'].browse(twin_id)
        if not twin.exists():
            raise UserError(_("Target digital twin not found"))

        try:
            # Validate package first
            if not self.validate_integrity():
                raise UserError(_("Package integrity validation failed"))

            # Decompress data
            decompressed_data = self.decompress_data()
            twin_data = json.loads(decompressed_data.decode('utf-8'))

            # Validate schema if available
            if not self.validate_schema(twin_data):
                raise UserError(_("Package schema validation failed"))

            # Extract based on content type
            if self.content_type == 'full_twin':
                result = self._apply_full_twin_data(twin, twin_data, merge_strategy)
            elif self.content_type == 'simulation_data':
                result = self._apply_simulation_data(twin, twin_data, merge_strategy)
            elif self.content_type == 'configuration':
                result = self._apply_configuration_data(twin, twin_data, merge_strategy)
            elif self.content_type == 'ai_insights':
                result = self._apply_ai_insights(twin, twin_data, merge_strategy)
            else:
                raise UserError(_("Unsupported content type for extraction: %s") % self.content_type)

            # Update package status
            self.write({
                'target_twin_id': twin_id,
                'package_status': 'extracted'
            })

            # Log success
            self.message_post(
                body=_("Package extracted to twin '%s' using %s strategy") % (twin.name, merge_strategy),
                message_type='notification'
            )

            return {
                'success': True,
                'twin_id': twin_id,
                'merge_strategy': merge_strategy,
                'records_updated': result.get('records_updated', 0),
                'size_extracted': len(decompressed_data)
            }

        except Exception as e:
            self.write({
                'package_status': 'error',
                'error_message': str(e)
            })
            _logger.error(f"Failed to extract package to twin {twin_id}: {str(e)}")
            raise UserError(_("Failed to extract package: %s") % str(e))

    # Data Extraction Methods
    def _extract_full_twin_data(self, twin):
        """Extract complete digital twin data"""
        return {
            'twin_info': {
                'name': twin.name,
                'description': twin.description,
                'domain_type': twin.domain_type,
                'industry_sector': twin.industry_sector,
                'twin_status': twin.twin_status
            },
            'configuration': json.loads(twin.twin_config) if twin.twin_config else {},
            'simulation_results': json.loads(twin.simulation_results) if twin.simulation_results else {},
            'ai_insights': json.loads(twin.ai_insights) if twin.ai_insights else {},
            'metrics': {
                'twin_health_score': twin.twin_health_score,
                'last_analysis_date': twin.last_analysis_date.isoformat() if twin.last_analysis_date else None,
                'simulation_count': twin.simulation_count
            },
            'simulations': [self._extract_simulation_record(sim) for sim in twin.simulation_ids],
            'created_date': twin.create_date.isoformat(),
            'package_created': fields.Datetime.now().isoformat()
        }

    def _extract_simulation_data(self, twin):
        """Extract simulation data only"""
        return {
            'twin_id': twin.id,
            'simulation_results': json.loads(twin.simulation_results) if twin.simulation_results else {},
            'simulations': [self._extract_simulation_record(sim) for sim in twin.simulation_ids],
            'metrics': {
                'simulation_count': twin.simulation_count,
                'last_analysis_date': twin.last_analysis_date.isoformat() if twin.last_analysis_date else None
            }
        }

    def _extract_configuration_data(self, twin):
        """Extract configuration data only"""
        return {
            'twin_id': twin.id,
            'configuration': json.loads(twin.twin_config) if twin.twin_config else {},
            'domain_type': twin.domain_type,
            'industry_sector': twin.industry_sector,
            'settings': {
                'auto_sync_bcm': twin.auto_sync_bcm,
                'enable_ai_analysis': twin.enable_ai_analysis,
                'enable_predictions': twin.enable_predictions
            }
        }

    def _extract_ai_insights(self, twin):
        """Extract AI insights only"""
        return {
            'twin_id': twin.id,
            'ai_insights': json.loads(twin.ai_insights) if twin.ai_insights else {},
            'prediction_models': json.loads(twin.prediction_models) if twin.prediction_models else {},
            'twin_health_score': twin.twin_health_score,
            'last_analysis_date': twin.last_analysis_date.isoformat() if twin.last_analysis_date else None
        }

    def _extract_simulation_record(self, simulation):
        """Extract data from a simulation record"""
        return {
            'id': simulation.id,
            'name': simulation.name if hasattr(simulation, 'name') else '',
            'status': simulation.state if hasattr(simulation, 'state') else '',
            'created_date': simulation.create_date.isoformat() if hasattr(simulation, 'create_date') else '',
            'results': simulation.results if hasattr(simulation, 'results') else {}
        }

    # Data Application Methods
    def _apply_full_twin_data(self, twin, data, merge_strategy):
        """Apply complete twin data"""
        updates = {}

        if 'twin_info' in data:
            if merge_strategy == 'replace':
                updates.update({
                    'description': data['twin_info'].get('description'),
                    'twin_status': data['twin_info'].get('twin_status')
                })

        if 'configuration' in data:
            if merge_strategy == 'replace':
                updates['twin_config'] = json.dumps(data['configuration'])
            elif merge_strategy == 'merge':
                existing_config = json.loads(twin.twin_config) if twin.twin_config else {}
                existing_config.update(data['configuration'])
                updates['twin_config'] = json.dumps(existing_config)

        if 'simulation_results' in data:
            updates['simulation_results'] = json.dumps(data['simulation_results'])

        if 'ai_insights' in data:
            updates['ai_insights'] = json.dumps(data['ai_insights'])

        if 'metrics' in data:
            metrics = data['metrics']
            if 'twin_health_score' in metrics:
                updates['twin_health_score'] = metrics['twin_health_score']

        twin.write(updates)
        return {'records_updated': 1}

    def _apply_simulation_data(self, twin, data, merge_strategy):
        """Apply simulation data"""
        updates = {}

        if 'simulation_results' in data:
            updates['simulation_results'] = json.dumps(data['simulation_results'])

        twin.write(updates)
        return {'records_updated': 1}

    def _apply_configuration_data(self, twin, data, merge_strategy):
        """Apply configuration data"""
        updates = {}

        if 'configuration' in data:
            if merge_strategy == 'replace':
                updates['twin_config'] = json.dumps(data['configuration'])
            elif merge_strategy == 'merge':
                existing_config = json.loads(twin.twin_config) if twin.twin_config else {}
                existing_config.update(data['configuration'])
                updates['twin_config'] = json.dumps(existing_config)

        if 'settings' in data:
            settings = data['settings']
            updates.update({
                'auto_sync_bcm': settings.get('auto_sync_bcm', twin.auto_sync_bcm),
                'enable_ai_analysis': settings.get('enable_ai_analysis', twin.enable_ai_analysis),
                'enable_predictions': settings.get('enable_predictions', twin.enable_predictions)
            })

        twin.write(updates)
        return {'records_updated': 1}

    def _apply_ai_insights(self, twin, data, merge_strategy):
        """Apply AI insights data"""
        updates = {}

        if 'ai_insights' in data:
            updates['ai_insights'] = json.dumps(data['ai_insights'])

        if 'prediction_models' in data:
            updates['prediction_models'] = json.dumps(data['prediction_models'])

        if 'twin_health_score' in data:
            updates['twin_health_score'] = data['twin_health_score']

        if 'last_analysis_date' in data and data['last_analysis_date']:
            updates['last_analysis_date'] = data['last_analysis_date']

        twin.write(updates)
        return {'records_updated': 1}

    # Action Methods
    def action_compress_test_data(self):
        """Test compression with sample data"""
        self.ensure_one()

        test_data = {
            'test': True,
            'message': 'BCM Digital Twin Package Test',
            'timestamp': fields.Datetime.now().isoformat(),
            'large_array': list(range(1000)),
            'nested_object': {
                'level1': {
                    'level2': {
                        'data': 'This is test data for compression efficiency testing' * 100
                    }
                }
            }
        }

        try:
            compressed_data, original_size, compressed_size = self.compress_data(test_data)

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Compression Test Successful"),
                    'message': _("Original: %d bytes, Compressed: %d bytes, Ratio: %.2f") % (
                        original_size, compressed_size, self.compression_ratio
                    ),
                    'type': 'success'
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Compression Test Failed"),
                    'message': str(e),
                    'type': 'danger'
                }
            }

    def action_validate_package(self):
        """Validate package integrity and schema"""
        self.ensure_one()

        try:
            integrity_valid = self.validate_integrity()
            schema_valid = self.validate_schema()

            if integrity_valid and schema_valid:
                status = 'success'
                message = _("Package validation successful")
            else:
                status = 'warning'
                message = _("Package validation failed: %s") % self.error_message

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Package Validation"),
                    'message': message,
                    'type': status
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Validation Error"),
                    'message': str(e),
                    'type': 'danger'
                }
            }

    def action_optimize_transport(self):
        """Optimize package for transport"""
        self.ensure_one()

        try:
            transport_config = self.optimize_for_transport()

            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Transport Optimization Complete"),
                    'message': _("Package optimized for %s priority transport") % self.network_priority,
                    'type': 'success'
                }
            }
        except Exception as e:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _("Optimization Failed"),
                    'message': str(e),
                    'type': 'danger'
                }
            }

    @api.model
    def get_compression_algorithms(self):
        """Get available compression algorithms with their capabilities"""
        algorithms = [
            {
                'code': 'none',
                'name': 'No Compression',
                'available': True,
                'speed': 'Fastest',
                'compression': 'None',
                'memory': 'Lowest'
            },
            {
                'code': 'gzip',
                'name': 'Gzip',
                'available': True,
                'speed': 'Fast',
                'compression': 'Good',
                'memory': 'Low'
            },
            {
                'code': 'zlib',
                'name': 'Zlib',
                'available': True,
                'speed': 'Fast',
                'compression': 'Good',
                'memory': 'Low'
            }
        ]

        if HAS_LZ4:
            algorithms.append({
                'code': 'lz4',
                'name': 'LZ4',
                'available': True,
                'speed': 'Fastest',
                'compression': 'Fair',
                'memory': 'Lowest'
            })

        if HAS_ZSTD:
            algorithms.append({
                'code': 'zstd',
                'name': 'Zstandard',
                'available': True,
                'speed': 'Balanced',
                'compression': 'Excellent',
                'memory': 'Medium'
            })

        if HAS_BROTLI:
            algorithms.append({
                'code': 'brotli',
                'name': 'Brotli',
                'available': True,
                'speed': 'Slower',
                'compression': 'Excellent',
                'memory': 'Higher'
            })

        return algorithms

    # Constraints and Validations
    @api.constrains('validation_schema')
    def _check_validation_schema(self):
        for record in self:
            if record.validation_schema:
                try:
                    json.loads(record.validation_schema)
                except ValueError:
                    raise ValidationError(_("Validation Schema must be valid JSON"))

    @api.constrains('transport_metadata')
    def _check_transport_metadata(self):
        for record in self:
            if record.transport_metadata:
                try:
                    json.loads(record.transport_metadata)
                except ValueError:
                    raise ValidationError(_("Transport Metadata must be valid JSON"))

    @api.constrains('compression_level')
    def _check_compression_level(self):
        for record in self:
            if record.compression_level < 1 or record.compression_level > 22:
                raise ValidationError(_("Compression level must be between 1 and 22"))

    # Model Lifecycle
    @api.model
    def create(self, vals):
        """Override create to set default schema"""
        if 'validation_schema' not in vals and vals.get('content_type'):
            vals['validation_schema'] = json.dumps(self._get_default_schema(vals['content_type']))

        return super().create(vals)

    def _get_default_schema(self, content_type):
        """Get default JSON schema for content type"""
        schemas = {
            'full_twin': {
                "type": "object",
                "properties": {
                    "twin_info": {"type": "object"},
                    "configuration": {"type": "object"},
                    "simulation_results": {"type": "object"},
                    "ai_insights": {"type": "object"},
                    "metrics": {"type": "object"},
                    "simulations": {"type": "array"},
                    "created_date": {"type": "string"},
                    "package_created": {"type": "string"}
                },
                "required": ["twin_info"]
            },
            'simulation_data': {
                "type": "object",
                "properties": {
                    "twin_id": {"type": "integer"},
                    "simulation_results": {"type": "object"},
                    "simulations": {"type": "array"},
                    "metrics": {"type": "object"}
                },
                "required": ["twin_id"]
            },
            'configuration': {
                "type": "object",
                "properties": {
                    "twin_id": {"type": "integer"},
                    "configuration": {"type": "object"},
                    "domain_type": {"type": "string"},
                    "industry_sector": {"type": "string"},
                    "settings": {"type": "object"}
                },
                "required": ["twin_id", "configuration"]
            },
            'ai_insights': {
                "type": "object",
                "properties": {
                    "twin_id": {"type": "integer"},
                    "ai_insights": {"type": "object"},
                    "prediction_models": {"type": "object"},
                    "twin_health_score": {"type": "number"},
                    "last_analysis_date": {"type": "string"}
                },
                "required": ["twin_id"]
            }
        }

        return schemas.get(content_type, {"type": "object"})