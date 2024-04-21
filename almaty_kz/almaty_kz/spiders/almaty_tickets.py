import scrapy
from scrapy.spiders import CrawlSpider
from almaty_kz.items import AlmatyKzItem


class AlmatyTicketsSpider(CrawlSpider):
    name = "almaty_tickets"
    purchase_url = 'https://purchase.almaty-arena.kz'
    ticket_url = 'https://purchase.almaty-arena.kz/webapi/tickets/timetable/'
    allowed_domains = ["almaty-arena.kz"]    

    def data_cheker(self, data):
        if isinstance(data, str):
            url_data = data.split('/')
            if 'purchase' in url_data:
                return 'purchase'
            if 'show' in url_data:
                return 'show'
            if 'event' in url_data:
                return 'event'

    def start_requests(self):
        url = getattr(self, "event_url", None)
        url_type = self.data_cheker(url)
        if url_type == 'purchase':
            yield scrapy.Request(url, self.parse)
        if url_type == 'show':
            yield scrapy.Request(url, self.parse_show)

    def parse_show(self, responce):
        purchase_link = responce.xpath("//div[@class='buy-ticket']/a/@href").get()
        link_type = self.data_cheker(purchase_link)
        if link_type == 'event':
            yield scrapy.Request(purchase_link, self.parse_event)
        else:
            yield scrapy.Request(purchase_link, self.parse)

    def parse_event(self, responce):
        purchase_link = responce.xpath('//div[@class="text-center"]/a/@href').get()
        yield scrapy.Request(self.purchase_url + purchase_link, self.parse)

    def parse(self, response):
        ev_id = response.url.split('/')[-1]
        yield scrapy.Request(self.ticket_url + ev_id, self.parse_purchase, meta={'id':ev_id})

    def parse_purchase(self, responce):
        data = responce.json()
        ev_id = responce.meta.get('id')
        for el in data:
            if el['ticket_type'] == 'seats':
                url = f'{self.ticket_url}{ev_id}/section/{el['section_id']}/seats'
                yield scrapy.Request(url, self.parse_seats, meta={'sec_name': el['section_name'], 'seat_type': el['ticket_type']})
            if el['ticket_type'] == 'sections':
                url = f'{self.ticket_url}{ev_id}/section/{el['section_id']}/sections'
                yield scrapy.Request(url, self.parse_seats, meta={'sec_name': el['section_name'], 'seat_type': el['ticket_type'], 'total':el['total']})
    
    def parse_seats(self, responce):
        data_seats = responce.json()['data']
        seat_type = responce.meta.get('seat_type')
        if seat_type == 'sections':
            yield AlmatyKzItem(
                sector = responce.meta.get('sec_name'),
                row = data_seats[0]['row'] if seat_type=='seats' else None,
                seat = data_seats[0]['seat'] if seat_type=='seats' else None,
                price = data_seats[0]['price'],
                count = responce.meta.get('total'),
                )
        else:
            for seat in data_seats:
                if int(seat.get('status')) == 1:
                    yield AlmatyKzItem(
                    sector = responce.meta.get('sec_name'),
                    row = seat['row'] if seat_type=='seats' else None,
                    seat = seat['seat'] if seat_type=='seats' else None,
                    price = seat['price'],
                    count = 1 if seat_type=='seats' else seat['seat'],
                    )
