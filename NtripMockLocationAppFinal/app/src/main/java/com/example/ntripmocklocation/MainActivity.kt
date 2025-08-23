package com.example.ntripmocklocation

import android.Manifest
import android.annotation.SuppressLint
import android.app.AppOpsManager
import android.content.Context
import android.content.Intent
import android.location.Location
import android.location.LocationManager
import android.os.Bundle
import android.os.Environment
import android.provider.Settings
import android.widget.Button
import android.widget.EditText
import android.widget.Switch
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import java.io.BufferedReader
import java.io.File
import java.io.FileWriter
import java.io.InputStreamReader
import java.net.Socket
import java.text.SimpleDateFormat
import java.util.*
import kotlin.concurrent.thread

class MainActivity : AppCompatActivity() {
    private lateinit var locationManager: LocationManager
    private lateinit var statusText: TextView
    private lateinit var locationText: TextView
    private lateinit var ipEditText: EditText
    private lateinit var portEditText: EditText
    private lateinit var connectButton: Button
    private lateinit var csvLoggingSwitch: Switch
    
    private var isConnecting = false
    private var shouldReconnect = true
    private var connectionThread: Thread? = null
    private var mockLocationThread: Thread? = null
    private var currentLatitude = 0.0
    private var currentLongitude = 0.0
    private var currentAltitude = 545.0
    private var mockProvidersInitialized = false
    
    private var csvWriter: FileWriter? = null
    private var csvFile: File? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // UI-Elemente initialisieren
        statusText = findViewById(R.id.statusText)
        locationText = findViewById(R.id.locationText)
        ipEditText = findViewById(R.id.ipEditText)
        portEditText = findViewById(R.id.portEditText)
        connectButton = findViewById(R.id.connectButton)
        csvLoggingSwitch = findViewById(R.id.csvLoggingSwitch)

        locationManager = getSystemService(Context.LOCATION_SERVICE) as LocationManager
        
        // Berechtigungen anfragen
        requestPermissions()

        // Connect Button Listener
        connectButton.setOnClickListener {
            if (isConnecting) {
                stopConnection()
            } else {
                startConnection()
            }
        }

        // Prüfe Standortdienste beim Start
        checkLocationServices()
    }

    private fun checkLocationServices() {
        try {
            val gpsEnabled = locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER)
            val networkEnabled = locationManager.isProviderEnabled(LocationManager.NETWORK_PROVIDER)
            
            // Detaillierte Provider-Analyse
            val allProviders = locationManager.getAllProviders()
            val enabledProviders = locationManager.getProviders(true)
            
            val statusMessage = when {
                gpsEnabled && networkEnabled -> 
                    "⚠️ GPS UND Network Provider aktiv! Für beste Mock Location deaktivieren"
                gpsEnabled -> 
                    "⚠️ GPS Provider aktiv! Für beste Mock Location deaktivieren"
                networkEnabled -> 
                    "⚠️ Network Provider aktiv! Für beste Mock Location deaktivieren"
                enabledProviders.isNotEmpty() -> 
                    "⚠️ Andere Provider aktiv: ${enabledProviders.joinToString(", ")}"
                else -> 
                    "✅ Keine echten Provider aktiv - Bereit für Mock Location"
            }
            
            statusText.text = statusMessage
            
            // Debug-Info für alle Provider
            println("Alle verfügbaren Provider: $allProviders")
            println("Aktivierte Provider: $enabledProviders")
            
        } catch (e: Exception) {
            statusText.text = "🔄 Bereit zum Verbinden (Provider-Check fehlgeschlagen)"
        }
    }

    private fun openLocationSettings() {
        try {
            val intent = Intent(Settings.ACTION_LOCATION_SOURCE_SETTINGS)
            startActivity(intent)
        } catch (e: Exception) {
            // Fallback zu allgemeinen Einstellungen
            try {
                val intent = Intent(Settings.ACTION_SETTINGS)
                startActivity(intent)
            } catch (e2: Exception) {
                // Konnte Einstellungen nicht öffnen
            }
        }
    }

    private fun requestPermissions() {
        val permissions = arrayOf(
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.WRITE_EXTERNAL_STORAGE
        )
        ActivityCompat.requestPermissions(this, permissions, 1001)
    }

    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        when (requestCode) {
            1001 -> {
                if (grantResults.isNotEmpty() && grantResults[0] == android.content.pm.PackageManager.PERMISSION_GRANTED) {
                    statusText.text = "🔄 Berechtigungen gewährt - Bereit zum Verbinden"
                } else {
                    statusText.text = "❌ Standort-Berechtigung für Mock Location erforderlich"
                }
            }
        }
    }

    private fun startConnection() {
        val ip = ipEditText.text.toString().trim()
        val portText = portEditText.text.toString().trim()
        
        if (ip.isEmpty() || portText.isEmpty()) {
            statusText.text = "❌ Bitte IP und Port eingeben"
            return
        }
        
        val port = portText.toIntOrNull()
        if (port == null || port <= 0 || port > 65535) {
            statusText.text = "❌ Ungültiger Port (1-65535)"
            return
        }

        isConnecting = true
        shouldReconnect = true
        connectButton.text = "Verbindung trennen"
        ipEditText.isEnabled = false
        portEditText.isEnabled = false
        
        connectToNtrip(ip, port)
    }

    private fun initializeCsvLogging() {
        if (!csvLoggingSwitch.isChecked) return
        
        try {
            val timeStamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.getDefault()).format(Date())
            val fileName = "GeoFix_Log_$timeStamp.csv"
            
            // Erstelle Datei im Downloads-Verzeichnis
            val downloadsDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
            csvFile = File(downloadsDir, fileName)
            csvWriter = FileWriter(csvFile!!)
            
            // CSV Header schreiben
            val header = "Timestamp,Latitude,Longitude,Altitude,RTK_Quality,Fix_Type,Satellites,HDOP,Quality_Assessment,Geoid_Height,DGPS_ID,Raw_NMEA\n"
            csvWriter?.write(header)
            csvWriter?.flush()
            
            runOnUiThread {
                statusText.text = "📊 GeoFix Log gestartet: $fileName"
            }
        } catch (e: Exception) {
            runOnUiThread {
                statusText.text = "❌ CSV-Logging Fehler: ${e.message}"
            }
        }
    }

    private fun logToCsv(
        lat: Double, lon: Double, altitude: String, fixQuality: String, fixType: String,
        satellites: String, hdop: String, qualityAssessment: String, geoidHeight: String,
        dgpsId: String, rawNmea: String
    ) {
        if (!csvLoggingSwitch.isChecked || csvWriter == null) return
        
        try {
            val timestamp = SimpleDateFormat("yyyy-MM-dd HH:mm:ss.SSS", Locale.getDefault()).format(Date())
            val csvLine = "$timestamp,$lat,$lon,\"$altitude\",$fixQuality,\"$fixType\",$satellites,$hdop,\"$qualityAssessment\",\"$geoidHeight\",$dgpsId,\"$rawNmea\"\n"
            csvWriter?.write(csvLine)
            csvWriter?.flush()
        } catch (e: Exception) {
            // CSV-Logging Fehler ignorieren, um die Hauptfunktion nicht zu beeinträchtigen
        }
    }

    private fun closeCsvLogging() {
        try {
            csvWriter?.close()
            csvWriter = null
            if (csvFile != null) {
                runOnUiThread {
                    statusText.text = "📊 GeoFix Log gespeichert: ${csvFile!!.name}"
                }
            }
        } catch (e: Exception) {
            // Fehler beim Schließen ignorieren
        }
    }

    private fun startContinuousMockLocation() {
        mockLocationThread = thread {
            while (shouldReconnect && !Thread.currentThread().isInterrupted()) {
                try {
                    if (currentLatitude != 0.0 && currentLongitude != 0.0) {
                        setMockLocation(currentLatitude, currentLongitude, currentAltitude)
                    }
                    Thread.sleep(1000) // Standard Updates: 1 Sekunde
                } catch (e: InterruptedException) {
                    break
                } catch (e: Exception) {
                    // Ignoriere Fehler und versuche weiter
                }
            }
        }
        
        runOnUiThread {
            statusText.text = "🛰️ Mock Location aktiv - Für beste Ergebnisse Flugzeugmodus aktivieren"
        }
    }

    private fun stopConnection() {
        shouldReconnect = false
        isConnecting = false
        connectionThread?.interrupt()
        connectionThread = null
        mockLocationThread?.interrupt()
        mockLocationThread = null
        
        // CSV-Logging schließen
        closeCsvLogging()
        
        // Koordinaten zurücksetzen
        currentLatitude = 0.0
        currentLongitude = 0.0
        currentAltitude = 545.0
        mockProvidersInitialized = false
        
        // Alle Test Provider bereinigen
        val providers = listOf(LocationManager.GPS_PROVIDER, LocationManager.NETWORK_PROVIDER)
        providers.forEach { provider ->
            try {
                locationManager.setTestProviderEnabled(provider, false)
                locationManager.removeTestProvider(provider)
            } catch (_: Exception) { 
                // Provider existiert möglicherweise nicht
            }
        }
        
        runOnUiThread {
            connectButton.text = "Verbinden"
            ipEditText.isEnabled = true
            portEditText.isEnabled = true
            statusText.text = "🔄 Verbindung getrennt"
            locationText.text = ""
        }
    }

    private fun connectToNtrip(ip: String, port: Int) {
        connectionThread = thread {
            var reconnectAttempts = 0
            val maxReconnectAttempts = 5
            val reconnectDelay = 3000L // 3 Sekunden
            
            while (shouldReconnect && !Thread.currentThread().isInterrupted()) {
                try {
                    runOnUiThread { 
                        statusText.text = if (reconnectAttempts == 0) {
                            "🔄 Verbinde mit $ip:$port..."
                        } else {
                            "🔄 Wiederverbindung... (Versuch $reconnectAttempts/$maxReconnectAttempts)"
                        }
                    }
                    
                    val socket = Socket(ip, port)
                    socket.soTimeout = 30000 // 30 Sekunden Timeout
                    val reader = BufferedReader(InputStreamReader(socket.getInputStream()))
                    
                    reconnectAttempts = 0 // Reset bei erfolgreicher Verbindung
                    runOnUiThread { statusText.text = "✅ GeoFix verbunden mit Server ($ip:$port)" }

                    // CSV-Logging initialisieren falls aktiviert
                    initializeCsvLogging()

                    // Starte kontinuierliche Mock Location Updates
                    startContinuousMockLocation()

                    while (shouldReconnect && !Thread.currentThread().isInterrupted()) {
                        val line = reader.readLine()
                        if (line == null) {
                            // Verbindung unterbrochen
                            throw Exception("Verbindung unterbrochen")
                        }
                        
                        if (line.startsWith("\$GNGGA") || line.startsWith("\$GPGGA")) {
                            val fields = line.split(",")
                            if (fields.size > 6 && fields[2].isNotEmpty() && fields[4].isNotEmpty()) {
                                val lat = convertToDecimal(fields[2], fields[3])
                                val lon = convertToDecimal(fields[4], fields[5])
                                
                                // RTK Fix Quality (Feld 6 in GNGGA)
                                val fixQuality = if (fields.size > 6) fields[6] else "0"
                                val fixType = when (fixQuality) {
                                    "0" -> "Kein Fix"
                                    "1" -> "GPS Fix"
                                    "2" -> "DGPS Fix"
                                    "4" -> "RTK Fixed"
                                    "5" -> "RTK Float"
                                    "6" -> "Estimated"
                                    "8" -> "Simulation"
                                    else -> "Unbekannt ($fixQuality)"
                                }
                                
                                // Anzahl Satelliten (Feld 7)
                                val satellites = if (fields.size > 7) fields[7] else "0"
                                
                                // HDOP - Horizontal Dilution of Precision (Feld 8)
                                val hdopValue = if (fields.size > 8 && fields[8].isNotEmpty()) {
                                    fields[8].toDoubleOrNull() ?: 0.0
                                } else 0.0
                                val hdop = if (fields.size > 8 && fields[8].isNotEmpty()) {
                                    String.format("%.1f", hdopValue)
                                } else "N/A"
                                
                                // Höhe über Meeresspiegel (Feld 9)
                                val altValue = if (fields.size > 9 && fields[9].isNotEmpty()) {
                                    fields[9].toDoubleOrNull() ?: 545.0
                                } else 545.0
                                val altitude = String.format("%.1f m", altValue)
                                
                                // Geoid-Höhe (Feld 11) 
                                val geoidHeight = if (fields.size > 11 && fields[11].isNotEmpty()) {
                                    val geoidValue = fields[11].toDoubleOrNull() ?: 0.0
                                    String.format("%.1f m", geoidValue)
                                } else "N/A"
                                
                                // DGPS Station ID (Feld 14)
                                val dgpsId = if (fields.size > 14 && fields[14].isNotEmpty()) {
                                    fields[14]
                                } else "N/A"
                                
                                // Qualitätsbewertung basierend auf HDOP
                                val qualityAssessment = when {
                                    hdop == "N/A" -> "Unbekannt"
                                    hdopValue <= 1.0 -> "Excellent"
                                    hdopValue <= 2.0 -> "Good"
                                    hdopValue <= 5.0 -> "Moderate"
                                    hdopValue <= 10.0 -> "Fair"
                                    else -> "Poor"
                                }

                                runOnUiThread {
                                    locationText.text = """
GPS-Position:
Lat: %.6f
Lon: %.6f
Alt: $altitude

RTK Status: $fixType
Satelliten: $satellites
HDOP: $hdop ($qualityAssessment)
Geoid-Höhe: $geoidHeight
DGPS ID: $dgpsId

Letzte Aktualisierung:
${System.currentTimeMillis()}
                                    """.trimIndent().format(lat, lon)
                                    
                                    // Aktualisiere die gespeicherten Koordinaten
                                    currentLatitude = lat
                                    currentLongitude = lon
                                    currentAltitude = altValue
                                    // Mock Location wird vom separaten Thread gesetzt
                                }
                                
                                // CSV-Logging falls aktiviert
                                logToCsv(lat, lon, altitude, fixQuality, fixType, satellites, hdop, qualityAssessment, geoidHeight, dgpsId, line)
                            }
                        }
                    }
                    
                    socket.close()
                    
                } catch (e: Exception) {
                    if (!shouldReconnect) break
                    
                    reconnectAttempts++
                    runOnUiThread { 
                        statusText.text = "❌ Verbindungsfehler: ${e.message}"
                    }
                    
                    if (reconnectAttempts >= maxReconnectAttempts) {
                        runOnUiThread { 
                            statusText.text = "❌ Max. Wiederverbindungsversuche erreicht"
                        }
                        stopConnection()
                        break
                    }
                    
                    // Warten vor erneutem Verbindungsversuch
                    try {
                        Thread.sleep(reconnectDelay)
                    } catch (ie: InterruptedException) {
                        break
                    }
                }
            }
        }
    }

    private fun convertToDecimal(value: String, direction: String): Double {
        val deg = value.substring(0, value.indexOf('.') - 2).toDouble()
        val min = value.substring(value.indexOf('.') - 2).toDouble()
        var result = deg + (min / 60.0)
        if (direction == "S" || direction == "W") result *= -1
        return result
    }

    @SuppressLint("MissingPermission")
    private fun initializeMockProviders() {
        if (mockProvidersInitialized) return
        
        try {
            val providers = listOf(LocationManager.GPS_PROVIDER, LocationManager.NETWORK_PROVIDER)
            
            providers.forEach { provider ->
                try {
                    // Entferne existierende Test Provider
                    try {
                        locationManager.setTestProviderEnabled(provider, false)
                        locationManager.removeTestProvider(provider)
                    } catch (_: Exception) { }

                    // Test Provider hinzufügen - einfache Version
                    locationManager.addTestProvider(
                        provider,
                        provider == LocationManager.NETWORK_PROVIDER, // requiresNetwork
                        provider == LocationManager.GPS_PROVIDER,     // requiresSatellite
                        false, // requiresCell
                        false, // hasMonetaryCost
                        true,  // supportsAltitude
                        true,  // supportsSpeed
                        true,  // supportsBearing
                        android.location.Criteria.POWER_MEDIUM,
                        android.location.Criteria.ACCURACY_FINE
                    )

                    // Provider aktivieren
                    locationManager.setTestProviderEnabled(provider, true)
                    
                } catch (e: Exception) {
                    // Provider-Fehler ignorieren
                }
            }
            
            mockProvidersInitialized = true
            
        } catch (e: Exception) {
            // Initialization Fehler ignorieren
        }
    }

    @SuppressLint("MissingPermission")
    private fun setMockLocation(latitude: Double, longitude: Double, altitude: Double = 545.0) {
        try {
            // Überprüfen ob Mock-Location-Berechtigung verfügbar ist
            val appOps = getSystemService(Context.APP_OPS_SERVICE) as AppOpsManager
            val mockLocationMode = appOps.checkOpNoThrow(
                AppOpsManager.OPSTR_MOCK_LOCATION,
                android.os.Process.myUid(),
                packageName
            )
            
            if (mockLocationMode != AppOpsManager.MODE_ALLOWED) {
                return // Stille Rückkehr ohne Fehlermeldung
            }

            // Provider nur einmal initialisieren
            initializeMockProviders()

            val currentTime = System.currentTimeMillis()
            val currentNanos = System.nanoTime()

            // Location für beide Provider setzen
            val providers = listOf(LocationManager.GPS_PROVIDER, LocationManager.NETWORK_PROVIDER)

            providers.forEach { provider ->
                try {
                    // Mock Location erstellen
                    val mockLocation = Location(provider).apply {
                        this.latitude = latitude
                        this.longitude = longitude
                        this.altitude = altitude
                        this.time = currentTime
                        this.accuracy = if (provider == LocationManager.GPS_PROVIDER) 2.0f else 50.0f
                        this.bearing = 0.0f
                        this.speed = 0.0f
                        
                        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.JELLY_BEAN_MR1) {
                            this.elapsedRealtimeNanos = currentNanos
                        }
                    }

                    // Location setzen
                    locationManager.setTestProviderLocation(provider, mockLocation)
                    
                } catch (e: Exception) {
                    // Provider-Fehler ignorieren
                }
            }
            
        } catch (e: Exception) {
            // Alle Fehler ignorieren für stabile Funktion
        }
    }

    // Hilfsklasse für Provider Properties
    private data class Tuple5<A, B, C, D, E>(val first: A, val second: B, val third: C, val fourth: D, val fifth: E)

    override fun onDestroy() {
        super.onDestroy()
        stopConnection()
    }
}
