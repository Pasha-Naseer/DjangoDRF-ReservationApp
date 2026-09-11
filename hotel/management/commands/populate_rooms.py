from django.core.management.base import BaseCommand
from hotel.models import Room, Hotel
from django.utils import timezone


class Command(BaseCommand):
    help = 'Populate the database with test rooms'

    def handle(self, *args, **kwargs):
        count = 6 # Number of test rooms to create
        rooms_to_create = []
        image_path = "room_image.jpg"
        self.stdout.write(f'Creating {count} test rooms...')

        for i in range(1, count+1):
            room = Room(
                name=f"اتاق شماره {i}",
                hotel=Hotel.objects.get(pk=1),
                description="لورم ایپسوم متن ساختگی با تولید سادگی نامفهوم از صنعت چاپ، و با استفاده از طراحان گرافیک است، چاپگرها و متون بلکه روزنامه و مجله در ستون و سطرآنچنان که لازم است، و برای شرایط فعلی تکنولوژی مورد نیاز، و کاربردهای متنوع با هدف بهبود ابزارهای کاربردی می باشد، کتابهای زیادی در شصت و سه درصد گذشته حال و آینده، شناخت فراوان جامعه و متخصصان را می طلبد، تا با نرم افزارها شناخت بیشتری را برای طراحان رایانه ای علی الخصوص طراحان خلاقی، و فرهنگ پیشرو در زبان فارسی ایجاد کرد، در این صورت می توان امید داشت که تمام و دشواری موجود در ارائه راهکارها، و شرایط سخت تایپ به پایان رسد و زمان مورد نیاز شامل حروفچینی دستاوردهای اصلی، و جوابگوی سوالات پیوسته اهل دنیای موجود طراحی اساسا مورد استفاده قرار گیرد.",
                image="room_image.jpg",
                image_1=image_path,
                image_2=image_path,
                image_3=image_path,
                image_4=image_path,
                price_per_night=300000,
                has_discount=True,
                discount=10,
            )
            rooms_to_create.append(room)
        
        print(rooms_to_create)
        # Bulk create for high performance
        Room.objects.bulk_create(rooms_to_create)

        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} rooms!'))
