window.CMS_MANUAL_INIT = true;

document.addEventListener('DOMContentLoaded', function() {
  var check = setInterval(function() {
    if (typeof CMS !== 'undefined') {
      clearInterval(check);
      CMS.init({ config: {
        backend: {
          name: 'github',
          repo: 'pixelatumente/carenas-guia',
          branch: 'main',
          base_url: 'https://auth.decapcms.org',
          auth_endpoint: '/auth',
        },
        media_folder: 'src/assets/photos',
        public_folder: '/images',
        locale: 'es',
        collections: [
          {
            name: 'datos',
            label: 'Base de datos',
            files: [
              {
                name: 'lugares',
                label: 'Todos los lugares',
                file: 'src/data/carenas.json',
                format: 'json',
                fields: [
                  { label: 'Lugares', name: 'places', widget: 'json' },
                ],
              },
            ],
          },
        ],
      } });
    }
  }, 100);
});
