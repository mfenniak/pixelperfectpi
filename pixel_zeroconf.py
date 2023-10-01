from zeroconf import ServiceStateChange
from zeroconf.asyncio import (
    AsyncServiceBrowser,
    AsyncServiceInfo,
    AsyncZeroconf,
)
import netifaces
import socket
import asyncio

class ZeroconfAdvertiser(object):
    async def start(self):
        self.zeroconf = AsyncZeroconf()
        self.browser = AsyncServiceBrowser(
            self.zeroconf.zeroconf, "_pixelperfectpi._tcp.local.", handlers=[self.async_on_service_state_change]
        )
        await self.register()

    async def register(self):
        hostname = socket.gethostname()
        info = AsyncServiceInfo(
            type_="_pixelperfectpi._tcp.local.",
            name=f"pixelperfectpi on {hostname}._pixelperfectpi._tcp.local.",
            parsed_addresses=self.get_addrs(),
            port=8080,
        )
        await self.zeroconf.async_register_service(info)
        print("Registered myself as a pixelperfectpi")

    def async_on_service_state_change(self, zeroconf, service_type, name, state_change):
        print(f"Service {name} of type {service_type} state changed: {state_change}")
        if state_change is not ServiceStateChange.Added:
            return
        asyncio.ensure_future(self.async_display_service_info(zeroconf, service_type, name))

    # This doesn't serve any real purpose in this app, except debugging.
    async def async_display_service_info(self, zeroconf, service_type, name):
        info = AsyncServiceInfo(service_type, name)
        await info.async_request(zeroconf, 3000)
        print("Info from zeroconf.get_service_info...")
        if info:
            addresses = ["%s:%d" % (addr, info.port) for addr in info.parsed_scoped_addresses()]
            print("  Name: %s" % name)
            print("  Addresses: %s" % ", ".join(addresses))
            print("  Weight: %d, priority: %d" % (info.weight, info.priority))
            print(f"  Server: {info.server}")
            if info.properties:
                print("  Properties are:")
                for key, value in info.properties.items():
                    print(f"    {key!r}: {value!r}")
            else:
                print("  No properties")
        else:
            print("  No info")
        print('\n')

    def get_addrs(self):
        interfaces = netifaces.interfaces()
        all_addrs = []
        for iface in interfaces:
            if iface == 'lo':
                continue
            addrs = netifaces.ifaddresses(iface)
            for ip4 in addrs.get(netifaces.AF_INET, []):
                addr = ip4.get("addr")
                if addr:
                    all_addrs.append(addr)
        return all_addrs
