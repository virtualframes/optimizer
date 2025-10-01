variable "gcp_project_id" {}
variable "gcs_image_path" {
  description = "The GCS path to the latest SyzygyOS image (e.g., gs://bucket/image.tar.gz)"
}

# 1. Create a GCE Image from the GCS artifact
resource "google_compute_image" "syzygyos_image" {
  # Use a unique name based on the image path hash to ensure updates
  name = "syzygyos-${substr(md5(var.gcs_image_path), 0, 10)}"
  family = "syzygy-os-custom"

  raw_disk {
    source = var.gcs_image_path
  }

  # Specify licenses required by GCE for custom NixOS images
  licenses = [
    "https://www.googleapis.com/compute/v1/projects/nixos-cloud/global/licenses/nixos"
  ]
}

# 2. Deploy the VM Instance
resource "google_compute_instance" "syzygy_core" {
  name         = "syzygy-core-immutable"
  machine_type = "e2-standard-8" # Adjust as needed
  zone         = "us-central1-a"

  # Ensure the VM waits for the image creation
  depends_on = [google_compute_image.syzygyos_image]

  boot_disk {
    initialize_params {
      # Use the custom image created above
      image = google_compute_image.syzygyos_image.self_link
      size  = 100
      type  = "pd-ssd"
    }
  }

  network_interface {
    network = "default"
    access_config { } # Public IP
  }
}