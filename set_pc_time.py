import ctypes
import ctypes.wintypes
import sys
from datetime import datetime

def set_pc_system_time():
    """Set PC system time - requires administrator privileges"""
    try:
        # Get current time
        current_time = datetime.now()
        
        # Define Windows SYSTEMTIME structure
        class SYSTEMTIME(ctypes.Structure):
            _fields_ = [
                ('wYear', ctypes.wintypes.WORD),
                ('wMonth', ctypes.wintypes.WORD),
                ('wDayOfWeek', ctypes.wintypes.WORD),
                ('wDay', ctypes.wintypes.WORD),
                ('wHour', ctypes.wintypes.WORD),
                ('wMinute', ctypes.wintypes.WORD),
                ('wSecond', ctypes.wintypes.WORD),
                ('wMilliseconds', ctypes.wintypes.WORD),
            ]

        # Fill the structure with current time
        st = SYSTEMTIME()
        st.wYear = current_time.year
        st.wMonth = current_time.month
        st.wDayOfWeek = current_time.weekday()
        st.wDay = current_time.day
        st.wHour = current_time.hour
        st.wMinute = current_time.minute
        st.wSecond = current_time.second
        st.wMilliseconds = current_time.microsecond // 1000

        # Call Windows API to set system time
        result = ctypes.windll.kernel32.SetSystemTime(ctypes.byref(st))
        
        if result:
            print(f"[OK] PC system time set to: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            return 0, f"PC time set to: {current_time.strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            error_code = ctypes.windll.kernel32.GetLastError()
            print(f"[ERROR] Failed to set PC system time. Error code: {error_code}")
            return 1, f"Failed to set PC time. Error: {error_code}"
            
    except Exception as e:
        print(f"Error setting PC system time: {e}")
        return 2, f"Error: {str(e)}"

def sync_pc_with_device_time():
    """Get device time and set PC to match it"""
    try:
        import os
        
        # Try multiple paths for the device DLL
        dll_paths = [
            r"C:\Program Files (x86)\IBDS\DataPilot\ReXdeskConvert\RgUSBdrv.dll",
            os.path.join(os.getcwd(), "ReXdeskConvert", "RgUSBdrv.dll"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "ReXdeskConvert", "RgUSBdrv.dll"),
            os.path.join(os.getcwd(), "dist", "RgUSBdrv.dll"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist", "RgUSBdrv.dll"),
            r"C:\Program Files (x86)\IBDS\DataPilot\dist\RgUSBdrv.dll",
            # Additional paths for PyInstaller executable running from dist folder
            os.path.join(os.getcwd(), "RgUSBdrv.dll"),  # Direct in current directory
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "RgUSBdrv.dll"),  # Same folder as script
        ]
        
        # If running as frozen executable, add executable directory paths
        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
            dll_paths.extend([
                os.path.join(exe_dir, "RgUSBdrv.dll"),  # Same folder as executable
                os.path.join(exe_dir, "ReXdeskConvert", "RgUSBdrv.dll"),  # ReXdeskConvert subfolder from exe
                os.path.join(exe_dir, "dist", "RgUSBdrv.dll"),  # dist subfolder from exe
                os.path.join(os.path.dirname(exe_dir), "ReXdeskConvert", "RgUSBdrv.dll"),  # Parent/ReXdeskConvert
                os.path.join(os.path.dirname(exe_dir), "dist", "RgUSBdrv.dll"),  # Parent/dist
            ])
            
        dll_path = None
        for path in dll_paths:
            if os.path.exists(path):
                dll_path = path
                print(f"Found DLL at: {dll_path}")
                break
                
        if dll_path is None:
            # Create detailed error message with all debugging info
            debug_info = [
                f"Device DLL not found. Debug information:",
                f"Current working directory: {os.getcwd()}",
                f"Script file path: {os.path.abspath(__file__)}",
                f"Running as frozen executable: {getattr(sys, 'frozen', False)}"
            ]
            
            if getattr(sys, 'frozen', False):
                debug_info.extend([
                    f"Executable path: {sys.executable}",
                    f"Executable directory: {os.path.dirname(sys.executable)}"
                ])
            
            debug_info.append(f"Checked {len(dll_paths)} paths:")
            for i, path in enumerate(dll_paths, 1):
                exists = "✓" if os.path.exists(path) else "✗"
                debug_info.append(f"  {i}. {exists} {path}")
            
            error_message = " | ".join(debug_info)
            return 3, error_message
            
        dll = ctypes.CDLL(dll_path)
        dll.GetDateTime.restype = ctypes.c_uint32
        dll.DeviceIsReady.restype = ctypes.c_ubyte
        
        # Check if device is ready
        if dll.DeviceIsReady() != 4:
            return 4, "Device not ready"
        
        # Get device time
        device_timestamp = dll.GetDateTime()
        device_time = datetime.fromtimestamp(device_timestamp)
        
        print(f"Device time: {device_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Set PC time to device time
        class SYSTEMTIME(ctypes.Structure):
            _fields_ = [
                ('wYear', ctypes.wintypes.WORD),
                ('wMonth', ctypes.wintypes.WORD),
                ('wDayOfWeek', ctypes.wintypes.WORD),
                ('wDay', ctypes.wintypes.WORD),
                ('wHour', ctypes.wintypes.WORD),
                ('wMinute', ctypes.wintypes.WORD),
                ('wSecond', ctypes.wintypes.WORD),
                ('wMilliseconds', ctypes.wintypes.WORD),
            ]

        st = SYSTEMTIME()
        st.wYear = device_time.year
        st.wMonth = device_time.month
        st.wDayOfWeek = device_time.weekday()
        st.wDay = device_time.day
        st.wHour = device_time.hour
        st.wMinute = device_time.minute
        st.wSecond = device_time.second
        st.wMilliseconds = device_time.microsecond // 1000

        result = ctypes.windll.kernel32.SetSystemTime(ctypes.byref(st))
        
        if result:
            print(f"[OK] PC time synced with device: {device_time.strftime('%Y-%m-%d %H:%M:%S')}")
            return 0, f"PC synced with device: {device_time.strftime('%Y-%m-%d %H:%M:%S')}"
        else:
            error_code = ctypes.windll.kernel32.GetLastError()
            return 5, f"Failed to sync PC time. Error: {error_code}"
            
    except Exception as e:
        return 6, f"Sync error: {str(e)}"

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "sync":
        exit_code, message = sync_pc_with_device_time()
    else:
        exit_code, message = set_pc_system_time()
    
    print(f"RESULT: {message}")
    sys.exit(exit_code) 