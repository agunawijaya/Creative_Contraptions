import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
import ghidra.app.decompiler.*;
import ghidra.util.task.ConsoleTaskMonitor;
import java.io.*;

public class DumpAll extends GhidraScript {
    public void run() throws Exception {
        String base = "C:/Projects/Creative_Contraptions/work/ghidra_out/";
        FunctionManager fm = currentProgram.getFunctionManager();
        PrintWriter fl = new PrintWriter(new FileWriter(base + "functions.txt"));
        DecompInterface ifc = new DecompInterface();
        ifc.openProgram(currentProgram);
        PrintWriter dc = new PrintWriter(new FileWriter(base + "decompiled.c"));
        int n = 0;
        for (Function f : fm.getFunctions(true)) {
            fl.println(f.getEntryPoint() + "  " + f.getName() +
                       "  size=" + f.getBody().getNumAddresses());
            DecompileResults r = ifc.decompileFunction(f, 60, new ConsoleTaskMonitor());
            if (r.decompileCompleted()) {
                dc.println("// ==== " + f.getName() + " @ " + f.getEntryPoint() + " ====");
                dc.println(r.getDecompiledFunction().getC());
                dc.println();
            }
            n++;
        }
        fl.println("\nTotal functions: " + n);
        fl.close();
        dc.close();
        println("DumpAll selesai: " + n + " fungsi");
    }
}
