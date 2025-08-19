import os
import ctypes
import time
import sys
from datetime import datetime
from ctypes import c_ubyte

def set_rexgen_time():
    """Set ReXgen device time using 32-bit DLL"""
    try:
        # Load the DLL from the full absolute path
        dll_path = r"C:\Program Files (x86)\IBDS\DataPilot\ReXdeskConvert\RgUSBdrv.dll"
        
        # Debug information
        print(f"Looking for DLL at: {dll_path}")
        print(f"Current working directory: {os.getcwd()}")
        print(f"DLL exists: {os.path.exists(dll_path)}")
        
        # Try alternative paths
        alternative_paths = [
            os.path.join(os.getcwd(), "ReXdeskConvert", "RgUSBdrv.dll"),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "ReXdeskConvert", "RgUSBdrv.dll"),
            r"C:\Program Files (x86)\IBDS\DataPilot\ReXdeskConvert\RgUSBdrv.dll",
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
            alternative_paths.extend([
                os.path.join(exe_dir, "RgUSBdrv.dll"),  # Same folder as executable
                os.path.join(exe_dir, "ReXdeskConvert", "RgUSBdrv.dll"),  # ReXdeskConvert subfolder from exe
                os.path.join(exe_dir, "dist", "RgUSBdrv.dll"),  # dist subfolder from exe
                os.path.join(os.path.dirname(exe_dir), "ReXdeskConvert", "RgUSBdrv.dll"),  # Parent/ReXdeskConvert
                os.path.join(os.path.dirname(exe_dir), "dist", "RgUSBdrv.dll"),  # Parent/dist
            ])
        
        dll_found = False
        for alt_path in alternative_paths:
            print(f"Checking alternative path: {alt_path}")
            if os.path.exists(alt_path):
                dll_path = alt_path
                dll_found = True
                print(f"Found DLL at: {dll_path}")
                break
        
        if not dll_found:
            # Create detailed error message with all debugging info
            debug_info = [
                f"DLL file not found. Debug information:",
                f"Current working directory: {os.getcwd()}",
                f"Script file path: {os.path.abspath(__file__)}",
                f"Running as frozen executable: {getattr(sys, 'frozen', False)}"
            ]
            
            if getattr(sys, 'frozen', False):
                debug_info.extend([
                    f"Executable path: {sys.executable}",
                    f"Executable directory: {os.path.dirname(sys.executable)}"
                ])
            
            debug_info.append(f"Checked {len(alternative_paths)} paths:")
            for i, path in enumerate(alternative_paths, 1):
                exists = "✓" if os.path.exists(path) else "✗"
                debug_info.append(f"  {i}. {exists} {path}")
            
            error_message = " | ".join(debug_info)
            return 1, error_message
        
        # Load the DLL
        dll = ctypes.CDLL(dll_path)

        # Define DLL function prototypes
        dll.DeviceIsReady.restype = c_ubyte
        dll.SetDateTime.argtypes = [ctypes.c_uint32]
        dll.SetDateTime.restype = c_ubyte
        dll.GetDateTime.restype = ctypes.c_uint32

        # Check if device is ready
        device_ready = dll.DeviceIsReady()
        print(f"DeviceIsReady result: {device_ready}")
        
        if device_ready == 4:
            # Get current local time
            local_time = datetime.now()
            utc_time = datetime.utcnow()
            
            # Add IST offset (5h 30m) to UTC time 
            ist_offset_seconds = 5 * 3600 + 30 * 60  # 5h 30m = 19800 seconds
            
            # Get UTC timestamp
            utc_timestamp = int(time.time())
            
            # Add IST offset so device will display correct local time
            # Send UTC + IST offset so device shows the right local time
            adjusted_timestamp = utc_timestamp + ist_offset_seconds
            
            # Also calculate actual timezone offset for comparison
            timezone_offset = int((local_time - utc_time).total_seconds())
            
            print(f"Local time: {local_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"UTC time: {utc_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Your timezone offset: {timezone_offset} seconds ({timezone_offset/3600:.1f} hours)")
            print(f"IST offset being added: {ist_offset_seconds} seconds (5.5 hours)")
            print(f"UTC timestamp: {utc_timestamp}")
            print(f"Adjusted timestamp: {adjusted_timestamp}")
            print(f"Adjusted timestamp as time: {datetime.fromtimestamp(adjusted_timestamp).strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Logic: Sending UTC + 5h30m to device")
            print(f"Sending adjusted timestamp to device...")
            
            unix_timestamp = adjusted_timestamp
            
            # Call the DLL function to set the device time
            result = dll.SetDateTime(unix_timestamp)
            
            if result == 0:
                print("[OK] Device time set successfully")
                
                # Verify the time was actually set by reading it back
                try:
                    time.sleep(1)  # Wait a moment for the device to process
                    device_timestamp = dll.GetDateTime()
                    device_time = datetime.fromtimestamp(device_timestamp).strftime('%Y-%m-%d %H:%M:%S')
                    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    
                    print(f"Device time after setting: {device_time}")
                    print(f"Current PC time: {current_time}")
                    
                    # Check if times are close (within 5 seconds)
                    time_diff = abs(device_timestamp - time.time())
                    if time_diff <= 5:
                        print("[OK] Device time verification successful")
                        return 0, f"Device time set and verified: {device_time}"
                    else:
                        print(f"[WARNING] Device time may not have been set correctly. Difference: {time_diff} seconds")
                        return 0, f"Time set but verification uncertain: {device_time}"
                        
                except Exception as verify_error:
                    print(f"[WARNING] Could not verify device time: {verify_error}")
                    return 0, "Time set but could not verify"
                    
            else:
                print(f"[ERROR] Failed to set device time. Return code: {result}")
                return 2, f"Failed to set device time. Return code: {result}"
        else:
            print("Device not ready for time setting")
            return 3, "Device not ready"
            
    except Exception as e:
        print(f"Error setting device time: {e}")
        return 4, f"Error: {str(e)}"

if __name__ == "__main__":
    exit_code, message = set_rexgen_time()
    print(f"RESULT: {message}")
    sys.exit(exit_code) 