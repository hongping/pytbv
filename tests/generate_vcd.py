
import sys

def create_vcd(filename):
    print(f"Generating {filename}...")
    with open(filename, 'w') as f:
        # Header
        f.write("$date\n    Jan 31 2026\n$end\n")
        f.write("$version\n    Ref VCD Generator\n$end\n")
        f.write("$timescale\n    1ns\n$end\n")
        f.write("$scope module top $end\n")
        f.write("$var wire 1 ! clk $end\n")
        f.write("$var wire 1 @ valid $end\n")
        f.write("$var wire 32 # addr $end\n")
        f.write("$var wire 8 $ data $end\n")
        f.write("$upscope $end\n")
        f.write("$enddefinitions $end\n")
        
        # Initial values
        f.write("$dumpvars\n0!\n0@\nb0 #\nb0 $\n$end\n")
        
        # Simulation
        # Grid is 5ns (half period). Period = 10ns.
        # Transactions at:
        # 1. Time 20ns (falling edge set), Sample at 25ns (rising edge)
        #    Addr=0x10, Data=0xAA
        # 2. Time 40ns set, Sample at 45ns
        #    Addr=0x20, Data=0xBB
        
        transactions = [
            (20, 0x10, 0xAA),
            (40, 0x20, 0xBB),
            (80, 0x30, 0xCC)
        ]
        
        current_time = 0
        clk = 0
        
        # Run for 200ns
        for i in range(40): # 40 * 5ns = 200ns
            current_time += 5
            
            # Toggle Clock
            clk = 1 - clk
            f.write(f"#{current_time}\n{clk}!\n")
            
            # Update Signals on Falling Edge (clk becomes 0)
            if clk == 0:
                # Check if a transaction starts or ends
                
                # Check start
                found_start = False
                for t_time, t_addr, t_data in transactions:
                    if current_time == t_time:
                        f.write(f"1@\nb{t_addr:b} #\nb{t_data:b} $\n")
                        found_start = True
                        break
                
                if not found_start:
                    # Check end (transaction held for 1 full cycle = 10ns? or just pulse?)
                    # Let's say we hold it for 10ns (one full period)
                    # If we started at T, we end at T+10?
                    # Actually, if we set at 20 (negedge), next negedge is 30.
                    
                    # Simple pulse approach: clear valid if not starting
                    # But we need to make sure we don't clear it immediately if we just set it?
                    # The loop steps by 5ns.
                    # 20ns: Set Valid.
                    # 25ns: Posedge (Sampled).
                    # 30ns: Negedge. Clear Valid.
                    f.write("0@\n")
                    
    print("Done.")

if __name__ == "__main__":
    create_vcd("tests/bus_protocol.vcd")
