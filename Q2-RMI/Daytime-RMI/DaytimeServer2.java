/**
 * DaytimeServer2.java
 *
 * Author: Daniel Lovegrove
 */

import java.io.*;
import java.rmi.*;
import java.rmi.registry.LocateRegistry;
import java.util.IllegalFormatException;
import java.util.Date;

public class DaytimeServer2 {
    public static void main(String[] args) {
        try {
            if (args.length != 1) throw new IllegalArgumentException("Expects one argument");
            int port = Integer.parseInt(args[0]);

            // Start the registry at the specified port
            LocateRegistry.createRegistry(port);
            System.out.println("Registry started.");

        } catch (NumberFormatException e) {
            System.out.println("Could not convert \"" + args[0] + "\" to an integer port number");
        } catch (RemoteException e) {
            System.out.println(e.getMessage());
        } catch (IllegalArgumentException e) {
            System.out.println("Expected one arguments. Call like:");
            System.out.println("\tjava DaytimeServer2 <port>");
        }
    }
}
