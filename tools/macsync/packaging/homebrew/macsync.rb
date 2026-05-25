class Macsync < Formula
  include Language::Python::Virtualenv

  desc "Personal Git-based sync manager for Mac nodes and an intranet Git hub"
  homepage "https://github.com/justinzjj/macsync"
  url "https://github.com/justinzjj/macsync/archive/refs/tags/v0.1.0.tar.gz"
  sha256 "CHANGE_ME_AFTER_TAGGING"
  license "MIT"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match "macsync", shell_output("#{bin}/macsync version")
  end
end

