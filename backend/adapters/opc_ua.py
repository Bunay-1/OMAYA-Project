"""
OPC-UA Adapter for OMAYA Platform
Provides connectivity to modern industrial controllers.
"""
from typing import Dict, Any, Optional, List
import logging
from datetime import datetime
import asyncio
from asyncua import Client, Node
from asyncua.common.methods import uamethod

logger = logging.getLogger(__name__)

class OPCUAAdapter:
    """
    OPC-UA Adapter for modern industrial controllers
    Supports reading/writing nodes, browsing, subscriptions
    """
    
    def __init__(self, endpoint_url: str, username: str = None, 
                 password: str = None, timeout: int = 10):
        """
        Initialize OPC-UA adapter.
        
        Args:
            endpoint_url: OPC-UA server endpoint URL (e.g., 'opc.tcp://localhost:4840')
            username: Optional username for authentication
            password: Optional password for authentication
            timeout: Connection timeout in seconds
        """
        self.endpoint_url = endpoint_url
        self.username = username
        self.password = password
        self.timeout = timeout
        self.client = None
        self.connected = False
        self.last_error: Optional[str] = None
        self.subscription = None
        
    async def connect(self) -> bool:
        """Establish connection to the OPC-UA server."""
        try:
            logger.info(f"Connecting to OPC-UA server at {self.endpoint_url}")
            self.client = Client(url=self.endpoint_url, timeout=self.timeout)
            
            if self.username and self.password:
                await self.client.connect_user(username=self.username, password=self.password)
            else:
                await self.client.connect()
            
            self.connected = True
            self.last_error = None
            logger.info(f"Successfully connected to OPC-UA server")
            return True
            
        except Exception as e:
            self.connected = False
            self.last_error = str(e)
            logger.error(f"Failed to connect to OPC-UA server: {e}")
            return False
    
    async def disconnect(self) -> bool:
        """Disconnect from OPC-UA server."""
        try:
            if self.subscription:
                await self.subscription.delete()
                self.subscription = None
                
            if self.client and self.connected:
                await self.client.disconnect()
                self.connected = False
                logger.info("Disconnected from OPC-UA server")
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from OPC-UA: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if connection is active."""
        return self.connected
    
    async def read_node(self, node_id: str) -> Optional[Any]:
        """
        Read value from a specific node.
        
        Args:
            node_id: Node ID (e.g., 'ns=2;s=Machine1.Temperature')
            
        Returns:
            Node value or None on error
        """
        if not self.connected:
            if not await self.connect():
                return None
        
        try:
            node = self.client.get_node(node_id)
            value = await node.read_value()
            logger.debug(f"Read node {node_id} = {value}")
            return value
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error reading node {node_id}: {e}")
            return None
    
    async def write_node(self, node_id: str, value: Any) -> bool:
        """
        Write value to a specific node.
        
        Args:
            node_id: Node ID
            value: Value to write
            
        Returns:
            True on success, False on error
        """
        if not self.connected:
            if not await self.connect():
                return False
        
        try:
            node = self.client.get_node(node_id)
            await node.write_value(value)
            logger.debug(f"Wrote node {node_id} = {value}")
            return True
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error writing node {node_id}: {e}")
            return False
    
    async def read_multiple_nodes(self, node_ids: List[str]) -> Dict[str, Optional[Any]]:
        """
        Read multiple nodes in one request.
        
        Args:
            node_ids: List of node IDs
            
        Returns:
            Dict mapping node IDs to values
        """
        if not self.connected:
            if not await self.connect():
                return {node_id: None for node_id in node_ids}
        
        results = {}
        try:
            nodes = [self.client.get_node(node_id) for node_id in node_ids]
            values = await asyncio.gather(*[node.read_value() for node in nodes], 
                                          return_exceptions=True)
            
            for node_id, value in zip(node_ids, values):
                if isinstance(value, Exception):
                    results[node_id] = None
                    logger.error(f"Error reading node {node_id}: {value}")
                else:
                    results[node_id] = value
                    
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error reading multiple nodes: {e}")
            results = {node_id: None for node_id in node_ids}
        
        return results
    
    async def browse_nodes(self, node_id: str = None) -> Optional[List[Dict[str, Any]]]:
        """
        Browse child nodes of a parent node.
        
        Args:
            node_id: Parent node ID (None for root)
            
        Returns:
            List of child node info dicts
        """
        if not self.connected:
            if not await self.connect():
                return None
        
        try:
            if node_id:
                parent = self.client.get_node(node_id)
            else:
                parent = self.client.get_root_node()
            
            children = []
            for child in await parent.get_children():
                child_id = child.nodeid.to_string()
                child_name = (await child.read_display_name()).Text
                child_browse_name = (await child.read_browse_name()).Name
                child_value = await child.read_value()
                
                children.append({
                    'node_id': child_id,
                    'display_name': child_name,
                    'browse_name': child_browse_name,
                    'value': child_value
                })
            
            return children
            
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error browsing nodes: {e}")
            return None
    
    async def call_method(self, object_id: str, method_id: str, 
                         *args) -> Optional[Any]:
        """
        Call a method on an object.
        
        Args:
            object_id: Object node ID
            method_id: Method node ID
            *args: Method arguments
            
        Returns:
            Method result or None on error
        """
        if not self.connected:
            if not await self.connect():
                return None
        
        try:
            obj = self.client.get_node(object_id)
            method = self.client.get_node(method_id)
            result = await obj.call_method(method, *args)
            return result
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error calling method: {e}")
            return None
    
    async def create_subscription(self, callback, interval: int = 1000) -> bool:
        """
        Create a subscription for data change notifications.
        
        Args:
            callback: Async callback function for data changes
            interval: Publishing interval in milliseconds
            
        Returns:
            True on success, False on error
        """
        if not self.connected:
            if not await self.connect():
                return False
        
        try:
            self.subscription = await self.client.create_subscription(interval, callback)
            logger.info(f"Created OPC-UA subscription with interval {interval}ms")
            return True
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error creating subscription: {e}")
            return False
    
    async def subscribe_node(self, node_id: str) -> Optional[Any]:
        """
        Subscribe to a node for data change notifications.
        
        Args:
            node_id: Node ID to subscribe
            
        Returns:
            Subscription handle or None on error
        """
        if not self.subscription:
            if not await self.create_subscription(lambda x: None):
                return None
        
        try:
            node = self.client.get_node(node_id)
            handle = await self.subscription.subscribe_data_change(node)
            logger.info(f"Subscribed to node {node_id}")
            return handle
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error subscribing to node: {e}")
            return None
    
    async def unsubscribe_node(self, handle) -> bool:
        """
        Unsubscribe from a node.
        
        Args:
            handle: Subscription handle
            
        Returns:
            True on success, False on error
        """
        if not self.subscription:
            return False
        
        try:
            await self.subscription.delete([handle])
            return True
        except Exception as e:
            logger.error(f"Error unsubscribing: {e}")
            return False
    
    async def get_node_attributes(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        Get all attributes of a node.
        
        Args:
            node_id: Node ID
            
        Returns:
            Dict of node attributes
        """
        if not self.connected:
            if not await self.connect():
                return None
        
        try:
            node = self.client.get_node(node_id)
            attributes = {
                'value': await node.read_value(),
                'display_name': (await node.read_display_name()).Text,
                'browse_name': (await node.read_browse_name()).Name,
                'node_class': await node.read_node_class(),
                'data_type': await node.read_data_type(),
                'description': (await node.read_description()).Text,
            }
            return attributes
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error reading node attributes: {e}")
            return None
    
    async def read_historical_data(self, node_id: str, start_time: datetime, 
                                  end_time: datetime) -> Optional[List[Dict[str, Any]]]:
        """
        Read historical data from a node (if supported).
        
        Args:
            node_id: Node ID
            start_time: Start time for historical data
            end_time: End time for historical data
            
        Returns:
            List of historical data points
        """
        if not self.connected:
            if not await self.connect():
                return None
        
        try:
            node = self.client.get_node(node_id)
            # Note: Historical data access requires server support
            # This is a simplified implementation
            logger.warning("Historical data access requires server-side support")
            return None
        except Exception as e:
            self.last_error = str(e)
            logger.error(f"Error reading historical data: {e}")
            return None
    
    async def get_server_status(self) -> Optional[Dict[str, Any]]:
        """Get server status information."""
        if not self.connected:
            if not await self.connect():
                return None
        
        try:
            status = {
                'endpoint_url': self.endpoint_url,
                'connected': True,
                'state': self.client.session.state if self.client.session else 'unknown',
                'timestamp': datetime.now().isoformat()
            }
            return status
        except Exception as e:
            logger.error(f"Error getting server status: {e}")
            return None
    
    def get_last_error(self) -> Optional[str]:
        """Get last error message."""
        return self.last_error
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.disconnect()
