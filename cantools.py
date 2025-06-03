import re

def print_dbc_signals_and_units():
    """Read the Microlite.dbc file and print all signals with their units"""
    
    try:
        # Read the DBC file as text and parse it manually
        with open('Microlite.dbc', 'r') as file:
            content = file.read()
        
        print("MICROLITE.DBC - SIGNALS AND UNITS")
        print("=" * 50)
        
        # Extract messages first
        message_pattern = r'BO_\s+(\d+)\s+(\w+):'
        messages = re.findall(message_pattern, content)
        
        
        print("\nSIGNALS AND UNITS:")
        print("-" * 50)
        
        # Extract signals and their units
        # Pattern for signals: SG_ SignalName : StartBit|Length@ByteOrder+ (Factor,Offset) [Min|Max] "Unit" Receivers
        signal_pattern = r'SG_\s+(\w+)\s*:\s*\d+\|\d+@\d+[+-]\s*\([^)]+\)\s*\[[^\]]+\]\s*"([^"]*)"'
        
        signals = re.findall(signal_pattern, content)
        
        if signals:
            for signal_name, unit in signals:
                unit_display = unit if unit else "No unit"
                print(f"  {signal_name:<30} : {unit_display}")
        else:
            print("No signals found with the expected pattern.")
            print("\nDBC file content preview:")
            print("-" * 30)
            print(content[:500] + "..." if len(content) > 500 else content)
                
    except FileNotFoundError:
        print("Error: Microlite.dbc file not found")
    except Exception as e:
        print(f"Error: {e}")

# Run the function
if __name__ == "__main__":
    print_dbc_signals_and_units()