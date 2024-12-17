#include <iostream>
#include <fstream>
#include <string>
#include <map>
#include <vector>
#include <cmath>
#include <ctime>
#include <sstream>
#include <functional>
#include <stdexcept>
#include <cctype>

const double D2R = M_PI / 180.0;

struct Satellite {
    std::string key;
    int prn;
    double elevation;
    double azimuth;
    double snr;
    std::string status;
    std::string system;
};

struct GPSState {
    std::time_t time;
    double lat;
    double lon;
    double alt;
    double speed;
    double track;
    double hdop;
    double pdop;
    double vdop;
    std::vector<Satellite> satsVisible;
    std::vector<int> satsActive;
    int fix;
    int systemId;
};

std::map<int, std::vector<int>> collectActiveSats;
std::map<std::string, Satellite> collectSats;
std::map<std::string, std::time_t> lastSeenSat;

bool isNumber(const std::string& str) {
    return !str.empty() && str.find_first_not_of("-0123456789.") == std::string::npos;
}

double parseCoord(const std::string& coord, char dir) {
    if (coord.empty() || !isNumber(coord)) {
        throw std::invalid_argument("Invalid coordinate string");
    }
    
    double value = std::stod(coord);
    int degrees = static_cast<int>(value) / 100;
    double minutes = value - (degrees * 100);
    double decimal = degrees + (minutes / 60.0);
    
    if (dir == 'S' || dir == 'W') {
        decimal *= -1;
    }
    
    return decimal;
}

double parseKnots(const std::string& knots) {
    if (knots.empty() || !isNumber(knots)) {
        throw std::invalid_argument("Invalid knots string");
    }
    
    return std::stod(knots) * 1.852;
}

std::string parseSystem(const std::string& str) {
    std::string satellite = str.substr(1, 2);
    if (satellite == "GP") return "GPS";
    if (satellite == "GQ") return "QZSS";
    if (satellite == "GL") return "GLONASS";
    if (satellite == "GA") return "Galileo";
    if (satellite == "GB") return "BeiDou";
    return "unknown";
}

std::map<std::string, std::string> parseNMEA(const std::string& nmea) {
    std::map<std::string, std::string> data;
    std::istringstream ss(nmea);
    std::string token;
    if (nmea[0] == '$') {
        std::getline(ss, token, ',');
        std::string type = token.substr(3);
        data["type"] = type;
        int fieldIndex = 0;
        while (std::getline(ss, token, ',')) {
            switch (type[0]) {
                case 'R': // RMC
                    if (fieldIndex == 1) data["time"] = token;
                    if (fieldIndex == 2) data["status"] = token;
                    if (fieldIndex == 3) data["lat"] = token;
                    if (fieldIndex == 4) data["latDir"] = token;
                    if (fieldIndex == 5) data["lon"] = token;
                    if (fieldIndex == 6) data["lonDir"] = token;
                    if (fieldIndex == 7) data["speed"] = token;
                    if (fieldIndex == 8) data["track"] = token;
                    break;
                case 'G': // GGA, GSA, GSV, etc.
                    if (type == "GGA") {
                        if (fieldIndex == 1) data["time"] = token;
                        if (fieldIndex == 2) data["lat"] = token;
                        if (fieldIndex == 3) data["latDir"] = token;
                        if (fieldIndex == 4) data["lon"] = token;
                        if (fieldIndex == 5) data["lonDir"] = token;
                        if (fieldIndex == 9) data["alt"] = token;
                    }
                    break;
                default:
                    break;
            }
            fieldIndex++;
        }
    }
    return data;
}

void updateState(GPSState& state, const std::map<std::string, std::string>& data, GPS* gps) {
    try {
        if (data.at("type") == "RMC" || data.at("type") == "GGA" || data.at("type") == "GLL" || data.at("type") == "GNS") {
            state.time = std::time(nullptr);
            if (data.count("lat") && data.count("latDir") && isNumber(data.at("lat")) && !data.at("latDir").empty()) {
                state.lat = parseCoord(data.at("lat"), data.at("latDir")[0]);
            }
            if (data.count("lon") && data.count("lonDir") && isNumber(data.at("lon")) && !data.at("lonDir").empty()) {
                state.lon = parseCoord(data.at("lon"), data.at("lonDir")[0]);
            }
            gps->emit("GGA");
        }

        if (data.at("type") == "HDT" && data.count("heading") && isNumber(data.at("heading"))) {
            state.track = std::stod(data.at("heading"));
            emit("HDT");
        }

        if (data.at("type") == "ZDA") {
            state.time = std::time(nullptr);
            emit("ZDA");
        }

        if (data.at("type") == "GGA" && data.count("alt") && isNumber(data.at("alt"))) {
            state.alt = std::stod(data.at("alt"));
            emit("GGA");
        }

        if (data.at("type") == "RMC") {
            if (data.count("speed") && isNumber(data.at("speed"))) {
                state.speed = parseKnots(data.at("speed"));
            }
            if (data.count("track") && isNumber(data.at("track"))) {
                state.track = std::stod(data.at("track"));
            }
            emit("RMC");
        }

        if (data.at("type") == "GSA" && data.count("systemId") && isNumber(data.at("systemId"))) {
            int systemId = std::stoi(data.at("systemId"));
            std::vector<int> satellites;
            if (data.count("satellites")) {
                std::istringstream ss(data.at("satellites"));
                std::string satellite;
                while (std::getline(ss, satellite, ',')) {
                    if (!satellite.empty() && isNumber(satellite)) {
                        satellites.push_back(std::stoi(satellite));
                    }
                }
            }
            collectActiveSats[systemId] = satellites;
            state.satsActive = satellites;
            emit("GSA");
        }

        if (data.at("type") == "GSV" && data.count("prn") && data.count("elevation") && data.count("azimuth") && data.count("snr") &&
            isNumber(data.at("prn")) && isNumber(data.at("elevation")) && isNumber(data.at("azimuth")) && isNumber(data.at("snr"))) {
            std::time_t now = std::time(nullptr);
            std::vector<Satellite> satellites;
            Satellite sat;
            sat.prn = std::stoi(data.at("prn"));
            sat.elevation = std::stod(data.at("elevation"));
            sat.azimuth = std::stod(data.at("azimuth"));
            sat.snr = std::stod(data.at("snr"));
            sat.system = parseSystem(data.at("system"));
            sat.key = data.at("prn");
            satellites.push_back(sat);
            collectSats[sat.key] = sat;
            lastSeenSat[sat.key] = now;
            state.satsVisible = satellites;
            emit("GSV");
        }
    } catch (const std::exception& e) {
        std::cerr << "Error updating state: " << e.what() << std::endl;
    }
}

std::tm parseTime(const std::string& time, const std::string& date = "") {
    if (time.empty()) {
        throw std::invalid_argument("Invalid time string");
    }
    
    std::tm ret = {};
    if (!date.empty()) {
        ret.tm_mday = std::stoi(date.substr(0, 2));
        ret.tm_mon = std::stoi(date.substr(2, 2)) - 1;
        ret.tm_year = std::stoi(date.substr(4, 2)) + 100;
    }
    
    ret.tm_hour = std::stoi(time.substr(0, 2));
    ret.tm_min = std::stoi(time.substr(2, 2));
    ret.tm_sec = std::stoi(time.substr(4, 2));

    return ret;
}

class GPS {
public:
    GPS() : state({}), events() {}
    
    void update(const std::string& line) {
        auto data = parseNMEA(line);
        updateState(state, data, this);
        updateState(state, data);
    }

    void updateFromFile(const std::string& filename) {
        std::ifstream infile(filename);
        if (!infile.is_open()) {
            throw std::runtime_error("Could not open file: " + filename);
        }

        std::string line;
        while (std::getline(infile, line)) {
            update(line);
        }
    }

    void on(const std::string& event, std::function<void(const GPSState&)> callback) {
        events[event] = callback;
    }

    void emit(const std::string& event) {
        if (events.find(event) != events.end()) {
            events[event](state);
        }
    }

private:
    GPSState state;
    std::map<std::string, std::function<void(const GPSState&)>> events;
};

int main() {
    GPS gps;
    gps.on("GGA", [](const GPSState& state) {
        std::cout << "Получены данные GGA: Высота = " << state.alt << " м" << std::endl;
    });

    try {
        gps.updateFromFile("data.gps");
    } catch (const std::exception& e) {
        std::cerr << e.what() << std::endl;
    }
    
    return 0;
}
