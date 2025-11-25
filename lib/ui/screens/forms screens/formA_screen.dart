import 'package:flutter/material.dart';
import 'package:inventur/ui/widgets/container_form.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';

class FormularioA extends StatelessWidget {
  const FormularioA({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        backgroundColor: Colors.white,
        body: Column(children: [
          Padding(
              padding: EdgeInsets.only(right: 1142.5.w, top: 149.6.h),
              child: SizedBox(
                height: 89.76.h,
                child: IconButton(
                  onPressed: () => Navigator.pop(context),
                  icon: Icon(
                    Icons.arrow_back,
                    size: 96.h,
                  ),
                  padding: EdgeInsets.only(bottom: 14.96.h),
                ),
              )),
          Padding(
            padding: EdgeInsets.symmetric(vertical: 29.92.h),
            child: Column(
              children: [
                Text(
                  'CATEGORIA A',
                  style: TextStyle(
                      color: const Color.fromARGB(255, 55, 111, 60),
                      fontSize: 80.64.w,
                      fontWeight: FontWeight.bold),
                ),
                Divider(
                  color: const Color.fromARGB(255, 55, 111, 60),
                  indent: 134.4.w,
                  endIndent: 134.4.w,
                ),
                SizedBox(
                  height: 5.984.h,
                ),
              ],
            ),
          ),
          Expanded(
              child: ListView(children: [
            const ContainerA(
              form: 'Comércio turístico',
              routeName: '/ComercioTuristico',
            ),

            const ContainerA(
              form: 'Informações básicas do município',
              routeName: '/InfoBasicas',
            ),
            const ContainerA(
              form: 'Locadoras de imóveis para temporadas',
              routeName: '/LocadoraDeImoveis',
            ),
            // const ContainerA(form: 'Compras especiais'),

            // const ContainerA(form: 'Representações diplomáticas'),
            // ExpansionTileA(titulo: 'Serviços', minhaLista: [
            //   Tilee(texto: 'Serviços bancários', routeName: '/Placeholder'),
            //   Tilee(texto: 'Serviços mecânicos e postos de combustível', routeName: '/Placeholder'),
            //   const SizedBox(),
            //   const SizedBox()
            // ]),
            ExpansionTileA(titulo: 'Rodoviário', minhaLista: const [
              Tilee(texto: 'Rodovia', routeName: '/Rodovia'),
              //Tilee(texto: 'Estação rodoviária', routeName: '/Placeholder'),
              SizedBox(),
              SizedBox(),
              SizedBox()
            ]),
            // ExpansionTileA(titulo: 'Ferroviário', minhaLista: [
            //   Tilee(texto: 'Ferrovia e metrovia', routeName: '/Placeholder'),
            //   Tilee(texto: 'Estação ferroviária', routeName: '/Placeholder'),
            //   const SizedBox(),
            //   const SizedBox()
            // ]),
            // ExpansionTileA(titulo: 'Aeroviário', minhaLista: [
            //   Tilee(texto: 'Aeroporto e campo de pouso', routeName: '/Placeholder'),
            //   Tilee(texto: 'Heliporto', routeName: '/Placeholder'),
            //   const SizedBox(),
            //   const SizedBox()
            // ]),
            // ExpansionTileA(titulo: 'Aquaviário', minhaLista: [
            //   Tilee(texto: 'Hidrovia', routeName: '/Placeholder'),
            //   Tilee(texto: 'Porto, pier, cais, etc', routeName: '/Placeholder'),
            //   const SizedBox(),
            //   const SizedBox()
            // ]),
            ExpansionTileA(
              titulo: 'Sistemas',
              minhaLista: const [
                SizedBox(),
                Tilee(
                    texto: 'Sistemas de segurança',
                    routeName: '/SistemaDeSeguranca'),
                // Tilee(
                //   texto: 'Sistemas de saúde', routeName: '/Placeholder'
                // ),
                SizedBox(),
                SizedBox(),
              ],
            ),

            /*ListTile(title: (Text('aiii', textAlign: TextAlign.center,
                 style: TextStyle(color: Color.fromARGB(255, 55, 111, 60) ),)),
               dense: true, selectedTileColor: Colors.grey,),*/
          ])),
        ]));
  }
}
