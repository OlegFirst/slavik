"""
BPMN XML Parser

Парсит BPMN 2.0 XML и извлекает элементы процесса
"""

import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# BPMN 2.0 namespace
BPMN_NS = {"bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL"}


class BPMNParser:
    """
    BPMN 2.0 XML Parser

    Извлекает процессы, activities, sequence flows из BPMN XML
    """

    @staticmethod
    def validate_bpmn_xml(bpmn_xml: str) -> bool:
        """
        Validate BPMN XML structure

        Returns:
            bool: True if valid BPMN 2.0 XML

        Raises:
            ValueError: If XML is invalid or not BPMN 2.0
        """
        try:
            root = ET.fromstring(bpmn_xml)

            # Check root tag
            if root.tag != "{http://www.omg.org/spec/BPMN/20100524/MODEL}definitions":
                raise ValueError(f"Invalid BPMN XML format. Root tag: {root.tag}")

            return True

        except ET.ParseError as e:
            raise ValueError(f"Invalid XML: {str(e)}")

    @staticmethod
    def parse_bpmn_xml(bpmn_xml: str) -> ET.Element:
        """
        Parse BPMN XML string

        Returns:
            ET.Element: Root element
        """
        BPMNParser.validate_bpmn_xml(bpmn_xml)
        return ET.fromstring(bpmn_xml)

    @staticmethod
    def find_start_events(root: ET.Element) -> List[ET.Element]:
        """
        Find all start events in process

        Returns:
            List[ET.Element]: List of startEvent elements
        """
        return root.findall(".//bpmn:startEvent", BPMN_NS)

    @staticmethod
    def find_end_events(root: ET.Element) -> List[ET.Element]:
        """Find all end events"""
        return root.findall(".//bpmn:endEvent", BPMN_NS)

    @staticmethod
    def find_user_tasks(root: ET.Element) -> List[ET.Element]:
        """Find all user tasks"""
        return root.findall(".//bpmn:userTask", BPMN_NS)

    @staticmethod
    def find_service_tasks(root: ET.Element) -> List[ET.Element]:
        """Find all service tasks"""
        return root.findall(".//bpmn:serviceTask", BPMN_NS)

    @staticmethod
    def find_element_by_id(root: ET.Element, element_id: str) -> Optional[ET.Element]:
        """
        Find element by ID

        Args:
            root: BPMN root element
            element_id: Element ID to find

        Returns:
            ET.Element or None
        """
        return root.find(f".//*[@id='{element_id}']", BPMN_NS)

    @staticmethod
    def get_outgoing_flows(element: ET.Element) -> List[str]:
        """
        Get outgoing sequence flow IDs from element

        Args:
            element: BPMN element (startEvent, userTask, etc)

        Returns:
            List[str]: List of outgoing sequence flow IDs
        """
        outgoing = element.findall("bpmn:outgoing", BPMN_NS)
        return [flow.text for flow in outgoing if flow.text]

    @staticmethod
    def get_incoming_flows(element: ET.Element) -> List[str]:
        """Get incoming sequence flow IDs"""
        incoming = element.findall("bpmn:incoming", BPMN_NS)
        return [flow.text for flow in incoming if flow.text]

    @staticmethod
    def find_sequence_flow(root: ET.Element, flow_id: str) -> Optional[ET.Element]:
        """
        Find sequence flow by ID

        Args:
            root: BPMN root element
            flow_id: Sequence flow ID

        Returns:
            ET.Element or None
        """
        return root.find(f".//bpmn:sequenceFlow[@id='{flow_id}']", BPMN_NS)

    @staticmethod
    def get_next_elements(root: ET.Element, current_element: ET.Element) -> List[Dict[str, Any]]:
        """
        Find next elements following current element via sequence flows

        Args:
            root: BPMN root element
            current_element: Current element

        Returns:
            List[Dict]: List of next elements with metadata
                [{
                    "element": ET.Element,
                    "id": str,
                    "name": str,
                    "type": str
                }]
        """
        next_elements = []

        # Get outgoing flows
        outgoing_flow_ids = BPMNParser.get_outgoing_flows(current_element)

        for flow_id in outgoing_flow_ids:
            # Find sequence flow
            seq_flow = BPMNParser.find_sequence_flow(root, flow_id)

            if seq_flow is not None:
                # Get target element
                target_ref = seq_flow.get("targetRef")

                if target_ref:
                    target_element = BPMNParser.find_element_by_id(root, target_ref)

                    if target_element is not None:
                        next_elements.append({
                            "element": target_element,
                            "id": target_ref,
                            "name": target_element.get("name", target_ref),
                            "type": BPMNParser.get_element_type(target_element)
                        })

        return next_elements

    @staticmethod
    def get_element_type(element: ET.Element) -> str:
        """
        Get element type from tag name

        Args:
            element: BPMN element

        Returns:
            str: Element type (e.g., "USER_TASK", "SERVICE_TASK", "START_EVENT")
        """
        tag = element.tag.split("}")[-1]  # Remove namespace

        # Convert camelCase to UPPER_CASE
        # userTask -> USER_TASK
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', tag)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).upper()

    @staticmethod
    def extract_process_info(bpmn_xml: str) -> Dict[str, Any]:
        """
        Extract high-level process information

        Returns:
            Dict with process metadata:
                {
                    "process_id": str,
                    "name": str,
                    "start_events": List[str],
                    "end_events": List[str],
                    "user_tasks": List[Dict],
                    "service_tasks": List[Dict],
                    "total_activities": int
                }
        """
        root = BPMNParser.parse_bpmn_xml(bpmn_xml)

        # Find process element
        process = root.find(".//bpmn:process", BPMN_NS)
        if process is None:
            raise ValueError("No process element found in BPMN XML")

        process_id = process.get("id", "unknown")
        process_name = process.get("name", process_id)

        # Extract elements
        start_events = BPMNParser.find_start_events(root)
        end_events = BPMNParser.find_end_events(root)
        user_tasks = BPMNParser.find_user_tasks(root)
        service_tasks = BPMNParser.find_service_tasks(root)

        return {
            "process_id": process_id,
            "name": process_name,
            "start_events": [e.get("id") for e in start_events],
            "end_events": [e.get("id") for e in end_events],
            "user_tasks": [
                {
                    "id": t.get("id"),
                    "name": t.get("name", t.get("id"))
                }
                for t in user_tasks
            ],
            "service_tasks": [
                {
                    "id": t.get("id"),
                    "name": t.get("name", t.get("id"))
                }
                for t in service_tasks
            ],
            "total_activities": len(user_tasks) + len(service_tasks)
        }

    @staticmethod
    def is_end_event(element: ET.Element) -> bool:
        """Check if element is end event"""
        return element.tag == "{http://www.omg.org/spec/BPMN/20100524/MODEL}endEvent"

    @staticmethod
    def is_gateway(element: ET.Element) -> bool:
        """Check if element is gateway (exclusive, parallel, inclusive)"""
        tag = element.tag
        return ("gateway" in tag.lower() or
                "exclusiveGateway" in tag or
                "parallelGateway" in tag or
                "inclusiveGateway" in tag)


# Convenience functions

def validate_bpmn(bpmn_xml: str) -> bool:
    """Validate BPMN XML"""
    return BPMNParser.validate_bpmn_xml(bpmn_xml)


def extract_process_metadata(bpmn_xml: str) -> Dict[str, Any]:
    """Extract process metadata"""
    return BPMNParser.extract_process_info(bpmn_xml)
