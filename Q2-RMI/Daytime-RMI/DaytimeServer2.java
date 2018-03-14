/**
 * DaytimeServer2.java
 *
 * Author: Daniel Lovegrove
 */

import java.io.*;
import java.rmi.*;
import java.rmi.registry.LocateRegistry;
import java.util.IllegalFormatException;
import java.net.MalformedURLException;
import java.util.Date;

public class DaytimeServer2 {
    private static int NUM_SECS = 1;

    public static void main(String[] args) {
        try {
            if (args.length != 1) throw new IllegalArgumentException("Expects one argument");
            int port = Integer.parseInt(args[0]);

            String currentDateUrl = "rmi://localhost:" + port + "/CurrentDate";

            // Start the registry at the specified port, in this process
            LocateRegistry.createRegistry(port);
            System.out.println("Registry started.");

            // Create an object in the registry
            System.out.println("Server starting. Updating date every " + NUM_SECS + " seconds.");
            while (true) {
                // Get the current date
                Date timestamp = new Date();
                String date = timestamp.toString();
                Naming.rebind(currentDateUrl, new CurrentDate(date));
                // Sleep
                Thread.sleep(NUM_SECS * 1000);
            }

        } catch (NumberFormatException e) {
            System.out.println("Could not convert \"" + args[0] + "\" to an integer port number");
        } catch (IllegalArgumentException e) {
            System.out.println("Expected one arguments. Call like:");
            System.out.println("\tjava DaytimeServer2 <port>");
        } catch (MalformedURLException e) {
            System.out.println(e.getMessage());
        } catch (ConnectException e) {
            System.out.println(e.getMessage());
        } catch (RemoteException e) {
            System.out.println(e.getMessage());
        } catch (InterruptedException e) {
            System.out.println(e.getMessage());
        }
    }
}
