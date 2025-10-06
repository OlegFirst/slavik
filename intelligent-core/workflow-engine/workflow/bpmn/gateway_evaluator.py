"""
BPMN Gateway Evaluator

Handles gateway logic (XOR, AND, OR)
"""

import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
import logging

from .parser import BPMNParser
from .expression_evaluator import ExpressionEvaluator

logger = logging.getLogger(__name__)

# BPMN namespace
BPMN_NS = {"bpmn": "http://www.omg.org/spec/BPMN/20100524/MODEL"}


class GatewayEvaluator:
    """
    Evaluates BPMN gateway conditions and determines next paths

    Gateway Types:
    - Exclusive Gateway (XOR): Choose ONE path based on condition
    - Parallel Gateway (AND): Fork to ALL paths OR join from ALL paths
    - Inclusive Gateway (OR): Choose ALL paths where condition = true
    """

    def __init__(self):
        self.expr_evaluator = ExpressionEvaluator()

    # ========== EXCLUSIVE GATEWAY (XOR) ==========

    async def evaluate_exclusive_gateway(
        self,
        root: ET.Element,
        gateway_element: ET.Element,
        instance_variables: Dict[str, Any]
    ) -> Optional[str]:
        """
        Evaluate Exclusive Gateway (XOR) - selects ONE outgoing flow

        Logic:
        1. Get all outgoing sequence flows
        2. Evaluate condition on each flow
        3. Return first flow where condition = true
        4. If no condition matches, return default flow (if specified)

        Args:
            root: BPMN root element
            gateway_element: Gateway element
            instance_variables: Process instance variables

        Returns:
            str: Flow ID to take (or None if no match)
        """
        gateway_id = gateway_element.get("id")
        logger.info(f"Evaluating Exclusive Gateway: {gateway_id}")

        # Get default flow (if specified)
        default_flow_id = gateway_element.get("default")

        # Get all outgoing flows
        outgoing_flow_ids = BPMNParser.get_outgoing_flows(gateway_element)

        # Evaluate each flow
        for flow_id in outgoing_flow_ids:
            # Skip default flow for now
            if flow_id == default_flow_id:
                continue

            # Get sequence flow element
            seq_flow = BPMNParser.find_sequence_flow(root, flow_id)
            if seq_flow is None:
                continue

            # Get condition
            condition_expr = self._get_flow_condition(seq_flow)

            if condition_expr:
                # Evaluate condition
                result = self.expr_evaluator.evaluate(condition_expr, instance_variables)

                logger.debug(
                    f"Flow {flow_id}: condition='{condition_expr}' "
                    f"result={result}"
                )

                if result:
                    logger.info(f"Exclusive Gateway {gateway_id}: taking flow {flow_id}")
                    return flow_id
            else:
                # No condition - treat as always true (unless it's default)
                logger.info(f"Exclusive Gateway {gateway_id}: taking unconditional flow {flow_id}")
                return flow_id

        # No condition matched - take default flow
        if default_flow_id:
            logger.info(f"Exclusive Gateway {gateway_id}: taking default flow {default_flow_id}")
            return default_flow_id

        logger.warning(f"Exclusive Gateway {gateway_id}: no matching condition and no default!")
        return None

    # ========== PARALLEL GATEWAY (AND) ==========

    async def evaluate_parallel_gateway_fork(
        self,
        gateway_element: ET.Element
    ) -> List[str]:
        """
        Evaluate Parallel Gateway (AND) - FORK

        Fork: ALL outgoing flows are taken

        Args:
            gateway_element: Gateway element

        Returns:
            List[str]: ALL outgoing flow IDs
        """
        gateway_id = gateway_element.get("id")
        outgoing_flow_ids = BPMNParser.get_outgoing_flows(gateway_element)

        logger.info(
            f"Parallel Gateway (FORK) {gateway_id}: "
            f"taking ALL {len(outgoing_flow_ids)} flows"
        )

        return outgoing_flow_ids

    async def check_parallel_gateway_join(
        self,
        gateway_element: ET.Element,
        completed_incoming_flows: List[str]
    ) -> bool:
        """
        Check if Parallel Gateway (AND) - JOIN is ready

        Join: Wait for ALL incoming flows to complete

        Args:
            gateway_element: Gateway element
            completed_incoming_flows: List of incoming flow IDs that completed

        Returns:
            bool: True if ALL incoming flows completed
        """
        gateway_id = gateway_element.get("id")
        incoming_flow_ids = BPMNParser.get_incoming_flows(gateway_element)

        # Check if ALL incoming flows completed
        all_completed = all(
            flow_id in completed_incoming_flows
            for flow_id in incoming_flow_ids
        )

        logger.info(
            f"Parallel Gateway (JOIN) {gateway_id}: "
            f"{len(completed_incoming_flows)}/{len(incoming_flow_ids)} flows completed. "
            f"Ready: {all_completed}"
        )

        return all_completed

    # ========== INCLUSIVE GATEWAY (OR) ==========

    async def evaluate_inclusive_gateway(
        self,
        root: ET.Element,
        gateway_element: ET.Element,
        instance_variables: Dict[str, Any]
    ) -> List[str]:
        """
        Evaluate Inclusive Gateway (OR) - selects ALL paths where condition = true

        Logic:
        1. Get all outgoing sequence flows
        2. Evaluate condition on each flow
        3. Return ALL flows where condition = true
        4. If no condition matches, return default flow

        Args:
            root: BPMN root element
            gateway_element: Gateway element
            instance_variables: Process instance variables

        Returns:
            List[str]: Flow IDs to take
        """
        gateway_id = gateway_element.get("id")
        logger.info(f"Evaluating Inclusive Gateway: {gateway_id}")

        default_flow_id = gateway_element.get("default")
        outgoing_flow_ids = BPMNParser.get_outgoing_flows(gateway_element)

        selected_flows = []

        # Evaluate each flow
        for flow_id in outgoing_flow_ids:
            if flow_id == default_flow_id:
                continue

            seq_flow = BPMNParser.find_sequence_flow(root, flow_id)
            if seq_flow is None:
                continue

            condition_expr = self._get_flow_condition(seq_flow)

            if condition_expr:
                result = self.expr_evaluator.evaluate(condition_expr, instance_variables)

                if result:
                    selected_flows.append(flow_id)
            else:
                # No condition - always take
                selected_flows.append(flow_id)

        # If no flows selected, take default
        if not selected_flows and default_flow_id:
            selected_flows.append(default_flow_id)

        logger.info(
            f"Inclusive Gateway {gateway_id}: "
            f"taking {len(selected_flows)} flows: {selected_flows}"
        )

        return selected_flows

    # ========== HELPERS ==========

    def _get_flow_condition(self, seq_flow_element: ET.Element) -> Optional[str]:
        """
        Extract condition expression from sequence flow

        BPMN format:
        <sequenceFlow id="Flow1">
          <conditionExpression>${approved == true}</conditionExpression>
        </sequenceFlow>

        Args:
            seq_flow_element: Sequence flow element

        Returns:
            str: Condition expression or None
        """
        # Check for conditionExpression element
        condition_elem = seq_flow_element.find("bpmn:conditionExpression", BPMN_NS)

        if condition_elem is not None and condition_elem.text:
            return condition_elem.text.strip()

        # Check for condition attribute (non-standard but sometimes used)
        condition_attr = seq_flow_element.get("condition")
        if condition_attr:
            return condition_attr

        return None

    @staticmethod
    def get_gateway_type(gateway_element: ET.Element) -> str:
        """
        Get gateway type from element tag

        Args:
            gateway_element: Gateway element

        Returns:
            str: "exclusiveGateway", "parallelGateway", or "inclusiveGateway"
        """
        tag = gateway_element.tag
        # Remove namespace
        if "}" in tag:
            tag = tag.split("}")[-1]

        return tag

    @staticmethod
    def is_gateway_fork(gateway_element: ET.Element) -> bool:
        """
        Check if gateway is a FORK (multiple outgoing flows)

        Args:
            gateway_element: Gateway element

        Returns:
            bool: True if FORK
        """
        outgoing = BPMNParser.get_outgoing_flows(gateway_element)
        incoming = BPMNParser.get_incoming_flows(gateway_element)

        # Fork: 1 incoming, multiple outgoing
        return len(incoming) == 1 and len(outgoing) > 1

    @staticmethod
    def is_gateway_join(gateway_element: ET.Element) -> bool:
        """
        Check if gateway is a JOIN (multiple incoming flows)

        Args:
            gateway_element: Gateway element

        Returns:
            bool: True if JOIN
        """
        outgoing = BPMNParser.get_outgoing_flows(gateway_element)
        incoming = BPMNParser.get_incoming_flows(gateway_element)

        # Join: multiple incoming, 1 outgoing
        return len(incoming) > 1 and len(outgoing) == 1
