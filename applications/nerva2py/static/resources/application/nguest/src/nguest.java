import java.awt.*;
import java.awt.event.*;
import java.awt.print.Book;
import java.awt.print.PageFormat;
import java.awt.print.Paper;
import java.awt.print.Printable;
import java.awt.print.PrinterException;
import java.awt.print.PrinterJob;

import javax.swing.*;
import javax.swing.border.Border;
import javax.print.PrintService;
import javax.print.attribute.HashPrintRequestAttributeSet;
import javax.print.attribute.PrintRequestAttributeSet;
import javax.print.attribute.standard.Copies;
import javax.print.attribute.standard.Media;
import javax.print.attribute.standard.MediaSizeName;
import javax.print.attribute.standard.OrientationRequested;
import javax.print.attribute.standard.PrinterName;

import com.sun.pdfview.PDFFile;
import com.sun.pdfview.PDFPage;
import com.sun.pdfview.PDFRenderer;

import java.beans.PropertyChangeEvent;
import java.beans.PropertyChangeListener;
import java.io.BufferedReader;
import java.io.ByteArrayInputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.UnsupportedEncodingException;
import java.net.URI;
import java.net.URISyntaxException;
import java.net.URLEncoder;
import java.nio.ByteBuffer;
import java.util.HashMap;
import java.util.Map;
import java.util.Properties;
import java.util.StringTokenizer;

/*
This file is part of the Nervatura Framework
http://www.nervatura.com
Copyright © 2011-2014, Csaba Kappel
License: LGPLv3
http://www.nervatura.com/nerva2py/default/licenses
*/

public class nguest {
	
	private static final String
		title = "Nervatura Client Additions",
		lb_help = "Help",
		lb_ver = "Ver.No:",
		lb_port = "Port:",
		lb_root = "Document directory:",
		lb_setdir = "Set directory",
		lb_tray_err = "TrayIcon could not be added.",
		lb_tray_no = "SystemTray is not supported.",
		lb_settings = "Settings",
		lb_start = "Enable",
		lb_start_ok = "The additions is allowed! Listening on port ",
		lb_start_err = "Couldn't start server:\n ",
		lb_stop = "Disable",
		lb_stop_ok = "The additions is disabled!",
		lb_exit = "Exit",
		lb_err_operation = "Error during the operation!",
		lb_err_not_found = "Error 404, file not found.",
		lb_err_not_oldname = "Error 404, missing filename.",
	    lb_err_not_newname = "Error 404, missing new filename.",
	    lb_err_forbidden = "FORBIDDEN: Reading file failed.",
	    lb_err_forbidden_no_list = "FORBIDDEN: No directory listing.",
	    lb_err_missing_printer = "Missing printer."
		;
	
	private static final String appname = "nervaguest";
	private static final String vernum = "0.9.130510";
	private static final String support_link = "http://nervatura.com";
	
	private static int port = 8080;
	private static File wwwroot = new File(System.getProperty("user.home"),appname);
	private static Boolean isRun = false;
	private static String defPaperSize = "a4";
	
	private static Properties prop;
	private static TrayIcon trayIcon;
	private static nano server;
	private static JFrame frm;
	private static JTextArea path;
	private static JButton cmd_start;
	private static JButton cmd_stop;
	
	private static final Map<String, String> MIME_TYPES;
    static {
        Map<String, String> mime = new HashMap<String, String>();
        mime.put("css", "text/css");
        mime.put("htm", "text/html");
        mime.put("html", "text/html");
        mime.put("xml", "text/xml");
        mime.put("txt", "text/plain");
        mime.put("asc", "text/plain");
        mime.put("gif", "image/gif");
        mime.put("jpg", "image/jpeg");
        mime.put("jpeg", "image/jpeg");
        mime.put("png", "image/png");
        mime.put("mp3", "audio/mpeg");
        mime.put("m3u", "audio/mpeg-url");
        mime.put("mp4", "video/mp4");
        mime.put("ogv", "video/ogg");
        mime.put("flv", "video/x-flv");
        mime.put("mov", "video/quicktime");
        mime.put("swf", "application/x-shockwave-flash");
        mime.put("js", "application/javascript");
        mime.put("pdf", "application/pdf");
        mime.put("doc", "application/msword");
        mime.put("ogg", "application/x-ogg");
        mime.put("zip", "application/octet-stream");
        mime.put("exe", "application/octet-stream");
        mime.put("class", "application/octet-stream");
        MIME_TYPES = mime;
    }
    
    private static final Map<String, MediaSizeName> PAPER_SIZES;
    static {
        Map<String, MediaSizeName> sizes = new HashMap<String, MediaSizeName>();
        sizes.put("a3", MediaSizeName.ISO_A3);
        sizes.put("a4", MediaSizeName.ISO_A4);
        sizes.put("a5", MediaSizeName.ISO_A5);
        sizes.put("letter", MediaSizeName.NA_LETTER);
        sizes.put("legal", MediaSizeName.NA_LEGAL);
        PAPER_SIZES = sizes;
    }
    
    public static void main(String[] args) {
        SwingUtilities.invokeLater(new Runnable() {
            public void run() {
            	loadProperties();
            	createSettings();
            	if (!SystemTray.isSupported()) {
                    System.out.println(lb_tray_no);
                    JOptionPane.showMessageDialog(null, lb_tray_no);
                    frm.setVisible(true);
                } else {
                	createSystemTray();
                }
            	if (isRun == true) {
            		startServer();	
            	}
            }
        });
    }
    
    private static void loadProperties() {
    	try {
    		prop = new Properties();
    		File propf = new File(System.getProperty("user.home"),"."+appname+".properties");
    		if(propf.exists()) {
    			prop.load(new FileInputStream(System.getProperty("user.home")+System.getProperty("file.separator")+"."+appname+".properties"));	
    		} else {
    			prop.store(new FileOutputStream(System.getProperty("user.home")+System.getProperty("file.separator")+"."+appname+".properties"), null);
    		}
    		
    		if (prop.getProperty("port")!=null) {
    			port = Integer.parseInt(prop.getProperty("port"));
    		}
    		if (prop.getProperty("wwwroot")!=null) {
    			wwwroot = new File(prop.getProperty("wwwroot"));
    		}
    		if (prop.getProperty("isRun")!=null) {
    			isRun = Boolean.parseBoolean(prop.getProperty("isRun"));
    		}
    		if (!wwwroot.exists()) {
    			wwwroot.mkdirs();
    			new File(wwwroot.getAbsolutePath(),"export").mkdirs();
    			new File(wwwroot.getAbsolutePath(),"import").mkdirs();
    		}
    		writeProperties();
    	} catch (IOException ex) {
    		ex.printStackTrace();
    	}
    }
    
    private static void writeProperties() {
    	try {
    		prop.setProperty("port", Integer.toString(port));
    		prop.setProperty("wwwroot", wwwroot.getAbsolutePath());
    		prop.setProperty("isRun", Boolean.toString(isRun));
    		prop.store(new FileOutputStream(System.getProperty("user.home")+System.getProperty("file.separator")+"."+appname+".properties"), null);
    	} catch (IOException ex) {
    		ex.printStackTrace();
    	}
    }
    
    private static void showSettings() {
    	frm.setVisible(true);
    }
    private static void startServer() {
    	try {
    		server = new nguest().new nano(port);
    		server.start();
    		isRun = true; writeProperties();
    		if (trayIcon != null) {
    			trayIcon.getPopupMenu().getItem(2).setEnabled(false);
        		trayIcon.getPopupMenu().getItem(3).setEnabled(true);	
    		}
    		if (cmd_start != null) {
    			cmd_start.setEnabled(false); cmd_stop.setEnabled(true);	
    		}
		}
		catch( IOException ioe ) {
			if (trayIcon != null) {
				trayIcon.displayMessage(title, lb_start_err + ioe, TrayIcon.MessageType.ERROR);	
			} else {
				System.err.println(lb_start_err + ioe );
				JOptionPane.showMessageDialog(null, lb_start_err + ioe );
			}
		}
    	if (trayIcon != null) {
    		trayIcon.displayMessage(title, lb_start_ok + port , TrayIcon.MessageType.INFO);	
    	} else {
    		System.err.println(lb_start_ok + port);
    		JOptionPane.showMessageDialog(null, lb_start_ok + port);
    	}
    }
    private static void stopServer() {
    	 if (server != null) {
    		 server.stop(); server = null;
    		 isRun = false; writeProperties();
    		 if (trayIcon != null) {
    			 trayIcon.displayMessage(title, lb_stop_ok, TrayIcon.MessageType.INFO);
        		 trayIcon.getPopupMenu().getItem(2).setEnabled(true);
         		 trayIcon.getPopupMenu().getItem(3).setEnabled(false); 
    		 } else {
    			 System.err.println(lb_stop_ok);
    	    	 JOptionPane.showMessageDialog(null, lb_stop_ok);
    		 }
    		 if (cmd_start != null) {
     			cmd_start.setEnabled(true); cmd_stop.setEnabled(false);	
     		}
    	 }
    }
    private static void closeAll() {
    	if (trayIcon != null) {
    		SystemTray.getSystemTray().remove(trayIcon);
    	}
        System.exit(0);
    }
    
    private static void showHelp() {
    	try {
            Desktop.getDesktop().browse(new URI("http://localhost:"+port+"/?cmd=help"));
		} catch (URISyntaxException | IOException ex) {
      
		}
    }
    
    private static void setDir() {
    	JFileChooser chooser = new JFileChooser(); 
        chooser.setCurrentDirectory(new java.io.File("."));
        chooser.setDialogTitle(lb_setdir);
        chooser.setFileSelectionMode(JFileChooser.DIRECTORIES_ONLY);
        chooser.setAcceptAllFileFilterUsed(false);
        if (chooser.showOpenDialog(null) == JFileChooser.APPROVE_OPTION) { 
        	wwwroot = chooser.getSelectedFile();
        	path.setText(wwwroot.getAbsolutePath());
        	writeProperties();
            }
    }
    
    private static WindowListener closeWindow = new WindowAdapter() {
        public void windowClosing(WindowEvent e) {
        	frm.setVisible(false);
        	if (trayIcon == null) {
        		System.exit(0);
        	}
        }
    };
    
    private static ActionListener listener = new ActionListener() {
        public void actionPerformed(ActionEvent e) {
        	String itemName = "";
        	if (e.getSource().getClass().getName()=="java.awt.MenuItem") {
        		itemName = ((MenuItem)e.getSource()).getName();
        	} else {
        		itemName = ((JButton)e.getSource()).getName();
        	}
        	switch (itemName) {
      	  		case "settings":
      	  			showSettings();
      	  			break;
      	  		case "start":
      	  		    startServer();	
      	  			break;
      	  		case "stop":
	      	  		stopServer();	
      	  			break;
      	  		case "setdir":
      	  		    setDir();
      	  			break;
      	  		case "help":
      	  			showHelp();
      	  			break;
      	  		case "exit":
      	  			closeAll();
      	  			break;
      	  		default:
        	}
        }
    };
    
    private static void createSettings() {
    	frm = new JFrame(title);
    	frm.addWindowListener(closeWindow);
    	frm.setSize(400, 200);
    	frm.setIconImage((new ImageIcon(nguest.class.getResource("favicon.png"), "Nervatura icon")).getImage());
    	frm.setLocationRelativeTo(null); frm.setResizable(false);
    	
    	java.awt.Container content = frm.getContentPane();
    	Border border = BorderFactory.createLineBorder(Color.lightGray);
        Border paddingBorder = BorderFactory.createEmptyBorder(3,3,3,3);
    	
    	JPanel headerPane = new JPanel();
        headerPane.setLayout(new FlowLayout(FlowLayout.CENTER));
        headerPane.setBorder(BorderFactory.createCompoundBorder(border,paddingBorder));
        
        JLabel lb_verno = new JLabel(lb_ver+" "+vernum);
        lb_verno.setBackground(Color.lightGray);lb_verno.setOpaque(true); 
        lb_verno.setBorder(BorderFactory.createCompoundBorder(border,paddingBorder));
        headerPane.add(lb_verno);
        
        JLabel lb_icon = new JLabel();
        lb_icon.setIcon((new ImageIcon(nguest.class.getResource("icon24_ntura.png"), "Nervatura icon")));
        headerPane.add(lb_icon);
        JLabel website = new JLabel();
        website.setText("<html><a style=\"text-decoration:none;\" href=\""+support_link+"\">Nervatura Framework</a></html>");
        website.setCursor(new Cursor(Cursor.HAND_CURSOR));
        website.addMouseListener(new MouseAdapter() {
            @Override
            public void mouseClicked(MouseEvent e) {
                    try {
                            Desktop.getDesktop().browse(new URI(support_link));
                    } catch (URISyntaxException | IOException ex) {
                      
                    }
            }
        });
        headerPane.add(website);
        
        content.add(headerPane, BorderLayout.NORTH);
    	
        JPanel settingsPane = new JPanel();
        settingsPane.setLayout(new FlowLayout(FlowLayout.LEFT));
        
        JLabel lb_portn = new JLabel(lb_port);
        lb_portn.setBackground(Color.lightGray);lb_portn.setOpaque(true); 
        lb_portn.setBorder(BorderFactory.createCompoundBorder(border,paddingBorder));
        settingsPane.add(lb_portn);
        
        JFormattedTextField nport = new JFormattedTextField();
        nport.setValue(new Integer(port));
        nport.setColumns(4);
        nport.addPropertyChangeListener( new PropertyChangeListener() {
			@Override
			public void propertyChange(PropertyChangeEvent evt) {
			    try
			    {
			    	port = Integer.parseInt(((JFormattedTextField) evt.getSource()).getText());
			    	writeProperties();
			    }
			    catch (NumberFormatException e)
			    {
			      return;
			    }
				
			}
		});
        nport.setBorder(BorderFactory.createCompoundBorder(border,paddingBorder));
        nport.setFont((new Font("Sans",Font.BOLD,12)));
        settingsPane.add(nport);
        
        JLabel lb_path = new JLabel(lb_root);
        lb_path.setBackground(Color.lightGray);lb_path.setOpaque(true); 
        lb_path.setBorder(BorderFactory.createCompoundBorder(border,paddingBorder));
        settingsPane.add(lb_path);
        
        JButton cmd_dir = new JButton("...");
        cmd_dir.setToolTipText(lb_setdir);
        cmd_dir.setName("setdir");
        cmd_dir.addActionListener(listener);
        settingsPane.add(cmd_dir);
        
        path = new JTextArea(3, 35);
        path.setText(wwwroot.getAbsolutePath());
        path.setLineWrap(true);path.setFont((new Font("Sans",Font.BOLD,11)));
        path.setEditable(false);
        settingsPane.add(path);
        
        settingsPane.setBorder(BorderFactory.createCompoundBorder(border,paddingBorder));
        content.add(settingsPane, BorderLayout.CENTER);
        
        JPanel cmdPane = new JPanel();
        
        cmd_start = new JButton(lb_start); cmd_start.setForeground(new Color(Integer.parseInt( "228B22",16)));
        cmd_start.setName("start"); cmd_start.setEnabled(server==null);
        cmd_start.addActionListener(listener);
        cmdPane.add(cmd_start);
        
        cmd_stop = new JButton(lb_stop); cmd_stop.setForeground(Color.red);
        cmd_stop.setName("stop"); cmd_stop.setEnabled(server!=null);
        cmd_stop.addActionListener(listener);
        cmdPane.add(cmd_stop);
        
        JLabel lb_sep = new JLabel("     ");
        cmdPane.add(lb_sep);
        
        JButton cmd_help = new JButton(lb_help);
        cmd_help.setName("help");
        cmd_help.addActionListener(listener);
        cmdPane.add(cmd_help);
        
        JButton cmd_exit = new JButton(lb_exit);
        cmd_exit.setName("exit");
        cmd_exit.addActionListener(listener);
        cmdPane.add(cmd_exit);
        cmdPane.setBorder(BorderFactory.createCompoundBorder(border,paddingBorder));
        content.add(cmdPane, BorderLayout.SOUTH);

    }
    
    private static void createSystemTray() {
        
        final PopupMenu popup = new PopupMenu();
        popup.setFont((new Font("Sans",Font.BOLD,12)));

        MenuItem settingsItem = new MenuItem(lb_settings);
        settingsItem.setName("settings"); popup.add(settingsItem);
        settingsItem.addActionListener(listener);
        
        popup.addSeparator();
        MenuItem startItem = new MenuItem(lb_start);
        startItem.setName("start"); popup.add(startItem);
        startItem.addActionListener(listener);
        
        MenuItem stopItem = new MenuItem(lb_stop);
        stopItem.setName("stop"); stopItem.setEnabled(false); popup.add(stopItem);
        stopItem.addActionListener(listener);
        
        popup.addSeparator();
        MenuItem exitItem = new MenuItem(lb_exit);
        exitItem.setName("exit"); popup.add(exitItem);
        exitItem.addActionListener(listener);
        
        trayIcon = new TrayIcon((new ImageIcon(nguest.class.getResource("favicon.png"), "Nervatura icon")).getImage());
        trayIcon.setImageAutoSize(true); trayIcon.setToolTip(title);
        trayIcon.setPopupMenu(popup);
        trayIcon.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e) {showSettings();}
        });
        try {
        	SystemTray.getSystemTray().add(trayIcon);
        } catch (AWTException e) {
            System.out.println(lb_tray_err);
            JOptionPane.showMessageDialog(null, lb_tray_err);
            return;
        }
    }
    
    private class PDFPrintPage implements Printable {

    	private PDFFile file;
    	
    	PDFPrintPage(PDFFile file) {
    		this.file = file;
    	}

    	public int print(Graphics g, PageFormat format, int index) throws PrinterException {
    		int pagenum = index + 1;
    		if ((pagenum >= 1) && (pagenum <= file.getNumPages())) {
    			Graphics2D g2 = (Graphics2D) g;
    			PDFPage page = file.getPage(pagenum);

    			Rectangle imageArea = new Rectangle((int) format.getImageableX(), (int) format.getImageableY(),
    					(int) format.getImageableWidth(), (int) format.getImageableHeight());
    			g2.translate(0, 0);
    			PDFRenderer pgs = new PDFRenderer(page, g2, imageArea, null, null);
    			try {
    				page.waitForFinish();
    				pgs.run();
    			} catch (InterruptedException ie) {
    			}
    			return PAGE_EXISTS;
    		} else {
    			return NO_SUCH_PAGE;
    		}
    	}
    }
    
    private class nano extends NanoHTTPD {
    	
    	public nano(int port) throws IOException {
    		super(port);
    	}
    	
    	private Response getVernum() {
    		return new NanoHTTPD.Response(NanoHTTPD.Response.Status.OK,MIME_PLAINTEXT,vernum);
    	}
    	
    	private Response showHelp() {
    		
    		StringBuffer sb = new StringBuffer();
    		BufferedReader br = null;
			try {
				br = new BufferedReader(new InputStreamReader(getClass().getResourceAsStream("help.html"), "UTF-8"));
			} catch (UnsupportedEncodingException e) {
				e.printStackTrace();
			}
    		try {
				for (int c = br.read(); c != -1; c = br.read()) sb.append((char)c);
			} catch (IOException e) {
				e.printStackTrace();
			}
    		
    		return new NanoHTTPD.Response(NanoHTTPD.Response.Status.OK, MIME_HTML, sb.toString());
    	}
    	
    	private Response exportToFile(String filename, String pfile, String edir, String encode) {
			if (edir==null)
				edir = "export";
			if (encode ==null)
				encode = "";
    		File dir;
    		try {
    			dir = new File(wwwroot.getAbsolutePath(), edir);	
    		} catch (Exception e){
    			dir = new File(wwwroot.getAbsolutePath(), "export");
    		}
    		if (!dir.exists()) {dir.mkdirs();}
    		
    		byte[] ba1 = new byte[1024];
    		int baLength; byte[] decodedBytes;
    		switch (encode) {
			case "base64":
				decodedBytes = Base64.decode(pfile);	
				break;
			default:
				decodedBytes = pfile.getBytes();
				break;
			}
    		try{
    			InputStream is = new ByteArrayInputStream(decodedBytes);
    			File file = new File(dir.getAbsolutePath(), filename);
    			FileOutputStream fos = new FileOutputStream(file);
    	        while ((baLength = is.read(ba1)) != -1) {
    	              fos.write(ba1, 0, baLength);
    	        }
    	        fos.flush();
    	        fos.close();
    	        is.close();
    		} catch (Exception e){
    			e.printStackTrace();
    		}
    		return new NanoHTTPD.Response(NanoHTTPD.Response.Status.OK,MIME_PLAINTEXT,"OK");
    	}
    	
    	private Response listFiles(String edir) {
    		String flist = "";
    		String[] files = null;
    		File dir = wwwroot;
    		if (edir!=null) {
        		dir = new File(wwwroot.getAbsolutePath(), edir);
        		if (dir!=null)
        			files = dir.list();
    		} else {
    			dir = wwwroot;
    			files = wwwroot.list();
    		}
    		if (files != null) {
                for (int i = 0; i < files.length; ++i) {
                	if (i>0) {flist +=",";}
                	File curFile = new File(dir, files[i]);
                    if (curFile.isDirectory()) {
                    	flist +="["+files[i]+"]";	
                    } else {
                    	flist +=files[i];
                    }
                }
    		}
    		return new NanoHTTPD.Response(NanoHTTPD.Response.Status.OK,MIME_PLAINTEXT,flist);
    	}
    	
    	private Response renameFile(String fdir, String filename, String ndir, String newname) {
    		String state = "OK";
    		File curFile;
    		if (filename==null)
    			return new Response(Response.Status.NOT_FOUND, NanoHTTPD.MIME_PLAINTEXT, lb_err_not_oldname);
    		if (newname==null)
    			return new Response(Response.Status.NOT_FOUND, NanoHTTPD.MIME_PLAINTEXT, lb_err_not_newname);
    		File filedir = null;
    		if (fdir==null) {
    			filedir = wwwroot;
    		} else {
    			filedir = new File(wwwroot.getAbsolutePath(), fdir);	
    		}
    		curFile = new File(filedir, filename);
    		if (!curFile.exists())
                return new Response(Response.Status.NOT_FOUND, NanoHTTPD.MIME_PLAINTEXT, lb_err_not_found);
    		File newdir = null;
    		if (ndir==null) {
    			newdir = filedir;
    		} else {
    			newdir = new File(wwwroot.getAbsolutePath(), ndir);
    			if (!newdir.exists())
    				newdir = filedir;
    		}
    		try {
    			if (!curFile.renameTo(new File(newdir, newname)))
    				state = lb_err_operation;
    		} catch (Exception e){
    			state = e.getMessage();
    		}
    		
    		return new NanoHTTPD.Response(NanoHTTPD.Response.Status.OK,MIME_PLAINTEXT,state);
    	}
    	
    	private Response deleteFile(String fdir, String filename) {
    		String state = "OK";
    		File curFile;
    		if (filename==null)
    			return new Response(Response.Status.NOT_FOUND, NanoHTTPD.MIME_PLAINTEXT, lb_err_not_oldname);
    		File filedir = null;
    		if (fdir==null) {
    			filedir = wwwroot;
    		} else {
    			filedir = new File(wwwroot.getAbsolutePath(), fdir);	
    		}
    		curFile = new File(filedir, filename);
    		if (!curFile.exists())
                return new Response(Response.Status.NOT_FOUND, NanoHTTPD.MIME_PLAINTEXT, lb_err_not_found);
    		try {
    			if (!curFile.delete())
    				state = lb_err_operation;
    		} catch (Exception e){
    			state = e.getMessage();
    		}
    		
    		return new NanoHTTPD.Response(NanoHTTPD.Response.Status.OK,MIME_PLAINTEXT,state);
    	}
    	
    	private Response uploadFile(Map<String, String> header, String fdir, String filename, String encode) {
    		if (encode==null)
    			encode="";
    		File curFile;
    		if (filename==null)
    			return new Response(Response.Status.NOT_FOUND, NanoHTTPD.MIME_PLAINTEXT, lb_err_not_oldname);
    		File filedir = null;
    		if (fdir==null) {
    			filedir = wwwroot;
    		} else {
    			filedir = new File(wwwroot.getAbsolutePath(), fdir);	
    		}
    		curFile = new File(filedir, filename);
    		if (!curFile.exists())
                return new Response(Response.Status.NOT_FOUND, NanoHTTPD.MIME_PLAINTEXT, lb_err_not_found);
    		switch (encode) {
			case "base64":
				byte[] b = new byte[(int)curFile.length()];
    			
    			FileInputStream fis;
				try {
					fis = new FileInputStream(curFile);
					fis.read(b);
					fis.close();
				} catch (IOException e) {
					e.printStackTrace();
				}
    			
    			String b64 =  Base64.encodeToString(b, true);
    			return new Response(Response.Status.OK, NanoHTTPD.MIME_PLAINTEXT, b64);

			default:
				return serveFile(header, curFile);
			}
    	}
    	
    	private String encodeUri(String uri) {
            String newUri = "";
            StringTokenizer st = new StringTokenizer(uri, "/ ", true);
            while (st.hasMoreTokens()) {
                String tok = st.nextToken();
                if (tok.equals("/"))
                    newUri += "/";
                else if (tok.equals(" "))
                    newUri += "%20";
                else {
                    try {
                        newUri += URLEncoder.encode(tok, "UTF-8");
                    } catch (UnsupportedEncodingException ignored) {
                    }
                }
            }
            return newUri;
        }
    	
    	private Response browseFiles(String uri, Map<String, String> header) {
    		Response res = null;
            uri = uri.trim().replace(File.separatorChar, '/');
            if (uri.indexOf('?') >= 0)
                uri = uri.substring(0, uri.indexOf('?'));

            File f = new File(wwwroot.getAbsolutePath(), uri);
            if (res == null && !f.exists())
                res = new Response(Response.Status.NOT_FOUND, NanoHTTPD.MIME_PLAINTEXT, lb_err_not_found);

            if (res == null && f.isDirectory()) {
                if (!uri.endsWith("/")) {
                    uri += "/";
                    res = new Response(Response.Status.REDIRECT, NanoHTTPD.MIME_HTML, "<html><body>Redirected: <a href=\"" + 
                      uri + "\">" + uri + "</a></body></html>");
                    res.addHeader("Location", uri);
                }

                if (res == null) {
                    if (new File(f, "index.html").exists())
                        f = new File(wwwroot.getAbsolutePath(), uri + "/index.html");
                    else if (new File(f, "index.htm").exists())
                        f = new File(wwwroot.getAbsolutePath(), uri + "/index.htm");
                    else if (f.canRead()) {
                        String[] files = f.list();
                        String msg = "<html><body><h1>Directory " + uri + "</h1><br/>";

                        if (uri.length() > 1) {
                            String u = uri.substring(0, uri.length() - 1);
                            int slash = u.lastIndexOf('/');
                            if (slash >= 0 && slash < u.length())
                                msg += "<b><a href=\"" + uri.substring(0, slash + 1) + "\">..</a></b><br/>";
                        }

                        if (files != null) {
                            for (int i = 0; i < files.length; ++i) {
                                File curFile = new File(f, files[i]);
                                boolean dir = curFile.isDirectory();
                                if (dir) {
                                    msg += "<b>";
                                    files[i] += "/";
                                }
                                msg += "<a href=\"" + encodeUri(uri + files[i]) + "\">" + files[i] + "</a>";
                                if (curFile.isFile()) {
                                    long len = curFile.length();
                                    msg += " &nbsp;<font size=2>(";
                                    if (len < 1024)
                                        msg += len + " bytes";
                                    else if (len < 1024 * 1024)
                                        msg += len / 1024 + "." + (len % 1024 / 10 % 100) + " KB";
                                    else
                                        msg += len / (1024 * 1024) + "." + len % (1024 * 1024) / 10 % 100 + " MB";
                                    msg += ")</font>";
                                }
                                msg += "<br/>";
                                if (dir)
                                    msg += "</b>";
                            }
                        }
                        msg += "</body></html>";
                        res = new Response(msg);
                    } else {
                        res = new Response(Response.Status.FORBIDDEN, NanoHTTPD.MIME_PLAINTEXT, lb_err_forbidden_no_list);
                    }
                }
            }
            if (res == null) {
            	return serveFile(header, f);
            } else {
            	res.addHeader("Accept-Ranges", "bytes");
                return res;	
            }
    	}
    	    	
    	private Response getPrinterSettings(String copies, String paper, String orientation) {
    		
    		String state = "";
    		Integer	cp = 1;
    		try  {cp = Integer.parseInt(copies);} 
    		catch(NumberFormatException nfe) {}
    		
    		String size = defPaperSize;
    		if (paper!=null)
    			if (PAPER_SIZES.containsKey(paper))
    				size = paper;
    		
    		PrinterJob pj = PrinterJob.getPrinterJob();    		
            PrintRequestAttributeSet aset = new HashPrintRequestAttributeSet();
            aset.add (new Copies (cp));
            aset.add(PAPER_SIZES.get(size));
            if (orientation!=null)
            	if (orientation.equals("landscape"))
            		aset.add(OrientationRequested.LANDSCAPE);
            	else
            		aset.add(OrientationRequested.PORTRAIT);
            else
            	aset.add(OrientationRequested.PORTRAIT);
            
            PageFormat pf = new PageFormat();
			pj.defaultPage(pf);
			
    		if (pj.printDialog(aset)) {	
    			if (aset.get(Media.class).toString().split("-").length>1)
    				size = aset.get(Media.class).toString().split("-")[1];
    			else
    				size = aset.get(Media.class).toString();
    			if (!PAPER_SIZES.containsKey(size))
    				size = defPaperSize;
    			state=pj.getPrintService().getAttributes().get(PrinterName.class).toString()
    					+"|"+aset.get(Copies.class).toString()
    					+"|"+size
    					+"|"+aset.get(OrientationRequested.class).toString();
    	    }
    		
    		return new NanoHTTPD.Response(NanoHTTPD.Response.Status.OK,MIME_PLAINTEXT,state);
    	}
    	
    	private Response printPdf(String filename, String pfile, String printer, String copies, String paper, String orientation, String encode) {
    		
    		if (filename==null)
    			filename = "Report";
    		if (pfile==null)
    	    	return new NanoHTTPD.Response(NanoHTTPD.Response.Status.NOT_FOUND,MIME_PLAINTEXT,lb_err_not_found);
    		if (printer==null)
    	    	return new NanoHTTPD.Response(NanoHTTPD.Response.Status.NOT_FOUND,MIME_PLAINTEXT,lb_err_missing_printer);
    		
    		String state = "OK";
    		Integer	cp = 1;
    		try  {cp = Integer.parseInt(copies);} 
    		catch(NumberFormatException nfe) {}
    		
    		String size = defPaperSize;
    		if (paper!=null)
    			if (PAPER_SIZES.containsKey(paper))
    				size = paper;
    		if (encode ==null)
    			encode = "";
    		
    		byte[] decodedBytes;
    		switch (encode) {
    		case "base64":
    			decodedBytes = Base64.decode(pfile);	
    			break;
    		default:
    			decodedBytes = pfile.getBytes();
    			break;
    		}
    		
    		InputStream is = new ByteArrayInputStream(decodedBytes);
    		byte[] pdfContent;
			try {
				pdfContent = new byte[is.available()];
				is.read(pdfContent, 0, is.available());
				ByteBuffer bb = ByteBuffer.wrap(pdfContent);
				
				PDFFile pdfFile = new PDFFile(bb);
				PDFPrintPage pages = new PDFPrintPage(pdfFile);
				
				PrinterJob pjob = PrinterJob.getPrinterJob();
				@SuppressWarnings("static-access")
				PrintService[] services = pjob.lookupPrintServices();
	    		for(PrintService ps:services){
	    		    String pName = ps.getName();
	    		    if(pName.equalsIgnoreCase(printer)){
	    		        try {
							pjob.setPrintService(ps);
						} catch (PrinterException e) {
							state = e.getMessage();
							return new NanoHTTPD.Response(NanoHTTPD.Response.Status.INTERNAL_ERROR,MIME_PLAINTEXT,state);
						}
	    		        break;
	    		    }
	    		}
	    		
				PageFormat pf = PrinterJob.getPrinterJob().defaultPage();
				pjob.setJobName(filename);
				Book book = new Book();
				book.append(pages, pf, pdfFile.getNumPages());
				pjob.setPageable(book);

				Paper pp = new Paper();
				pp.setImageableArea(0, 0, pp.getWidth(), pp.getHeight());
				pf.setPaper(pp);
	    		
	    		PrintRequestAttributeSet aset = new HashPrintRequestAttributeSet();
	    	    aset.add(new Copies (cp));
	    	    aset.add(PAPER_SIZES.get(size));
	    	    if (orientation!=null)
	    	    	if (orientation.equals("landscape"))
	    	    		aset.add(OrientationRequested.LANDSCAPE);
	    	    	else
	    	    		aset.add(OrientationRequested.PORTRAIT);
	    	    else
	    	    	aset.add(OrientationRequested.PORTRAIT);
				try {
					pjob.print(aset);
				} catch (PrinterException e) {
					state = e.getMessage();
					return new NanoHTTPD.Response(NanoHTTPD.Response.Status.INTERNAL_ERROR,MIME_PLAINTEXT,state);
				}
			} catch (IOException e1) {
				state = e1.getMessage();
				return new NanoHTTPD.Response(NanoHTTPD.Response.Status.INTERNAL_ERROR,MIME_PLAINTEXT,state);
			}
    		return new NanoHTTPD.Response(NanoHTTPD.Response.Status.OK,MIME_PLAINTEXT,state);
    	}
    	
    	private Response serveFile(Map<String, String> header, File f) {
    		Response res = null;
    		try {
                String mime = null;
                int dot = f.getCanonicalPath().lastIndexOf('.');
                if (dot >= 0)
                    mime = MIME_TYPES.get(f.getCanonicalPath().substring(dot + 1).toLowerCase());
                if (mime == null)
                    mime = NanoHTTPD.MIME_DEFAULT_BINARY;

                String etag = Integer.toHexString((f.getAbsolutePath() + f.lastModified() + "" + f.length()).hashCode());

                long startFrom = 0;
                long endAt = -1;
                String range = header.get("range");
                if (range != null) {
                    if (range.startsWith("bytes=")) {
                        range = range.substring("bytes=".length());
                        int minus = range.indexOf('-');
                        try {
                            if (minus > 0) {
                                startFrom = Long.parseLong(range.substring(0, minus));
                                endAt = Long.parseLong(range.substring(minus + 1));
                            }
                        } catch (NumberFormatException ignored) {
                        }
                    }
                }

                long fileLen = f.length();
                if (range != null && startFrom >= 0) {
                    if (startFrom >= fileLen) {
                        res = new Response(Response.Status.RANGE_NOT_SATISFIABLE, NanoHTTPD.MIME_PLAINTEXT, "");
                        res.addHeader("Content-Range", "bytes 0-0/" + fileLen);
                        res.addHeader("ETag", etag);
                    } else {
                        if (endAt < 0)
                            endAt = fileLen - 1;
                        long newLen = endAt - startFrom + 1;
                        if (newLen < 0)
                            newLen = 0;

                        final long dataLen = newLen;
                        FileInputStream fis = new FileInputStream(f) {
                            @Override
                            public int available() throws IOException {
                                return (int) dataLen;
                            }
                        };
                        fis.skip(startFrom);

                        res = new Response(Response.Status.PARTIAL_CONTENT, mime, fis);
                        res.addHeader("Content-Length", "" + dataLen);
                        res.addHeader("Content-Range", "bytes " + startFrom + "-" + endAt + "/" + fileLen);
                        res.addHeader("ETag", etag);
                    }
                } else {
                    if (etag.equals(header.get("if-none-match")))
                        res = new Response(Response.Status.NOT_MODIFIED, mime, "");
                    else {
                        res = new Response(Response.Status.OK, mime, new FileInputStream(f));
                        res.addHeader("Content-Length", "" + fileLen);
                        res.addHeader("ETag", etag);
                    }
                }
            } catch (IOException ioe) {
                res = new Response(Response.Status.FORBIDDEN, NanoHTTPD.MIME_PLAINTEXT, lb_err_forbidden);
            }

            res.addHeader("Accept-Ranges", "bytes");
            return res;
    	}
    	
    	@Override
    	public Response serve(String uri, Method method, Map<String, String> header, Map<String, String> parms, Map<String, String> files) {	
    		if (parms.get("cmd")!=null) {
    			switch (parms.get("cmd")) {
        		case "help":
        			return showHelp();
        		case "vernum":
        			return getVernum();
        		case "export":
    				return exportToFile(parms.get("filename"),parms.get("file"),parms.get("dir"),parms.get("encode"));
        		case "list":
    				return listFiles(parms.get("dir"));
        		case "rename":
    				return renameFile(parms.get("fdir"),parms.get("filename"),parms.get("ndir"),parms.get("newname"));
        		case "delete":
    				return deleteFile(parms.get("dir"),parms.get("filename"));
        		case "upload":
    				return uploadFile(header, parms.get("dir"),parms.get("filename"),parms.get("encode"));
        		case "printers":
        			return getPrinterSettings(parms.get("copies"),parms.get("size"),parms.get("orientation"));
        		case "print":
        			return printPdf(parms.get("filename"),parms.get("file"),parms.get("printer"),parms.get("copies"),parms.get("size"),parms.get("orientation"),parms.get("encode"));
        		default:
        			return showHelp();
            		
        		}
    		}
    		return browseFiles(uri, header);
    	}
    }
}

