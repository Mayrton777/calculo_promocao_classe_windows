import config
from app import AppView, AppController

if __name__ == "__main__":
    default_path = config.get_default_download_path()
    ufs_list = config.UFS
    classes_list = config.CLASSES
    lat = config.PLACEHOLDER_LAT
    lon = config.PLACEHOLDER_LON

    view = AppView(
        themename="litera",
        title="Promoção de Classe",
        ufs=ufs_list,
        classes=classes_list,
        default_path=default_path,
        placeholder_lat=lat,
        placeholder_lon=lon
    )

    controller = AppController(view)

    view.set_controller(controller)

    view.mainloop()