#include "dashboard.h"

using namespace esphome::dashboard;

static const char *const TAG = "dashboard";

Dashboard::Dashboard(): ESPDash()
{
}

void Dashboard::setup() {
  server_ = new AsyncWebServer(port_);
  ESPDash::init(server_);
  server_->begin();
}
void Dashboard::dump_config() {

}
void Dashboard::set_port(uint16_t port) {
  port_ = port;
}
